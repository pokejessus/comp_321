"""Run every submission against every test case and print a verdict table.
"""
import glob
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = 1.0
JSON_OUT = None
args = sys.argv[1:]
while args:
    if args[0] == "--tl":
        TL = float(args[1]); args = args[2:]
    elif args[0] == "--json":
        JSON_OUT = args[1]; args = args[2:]
    else:
        raise SystemExit(__doc__)

build = tempfile.mkdtemp(prefix="awkward_build_")


def prepare(path):
    """Return the command list that runs this submission, compiling if needed."""
    name = os.path.basename(path)
    base, ext = os.path.splitext(name)
    if ext == ".cpp":
        exe = os.path.join(build, base + "_" + os.path.basename(os.path.dirname(path)))
        subprocess.run(["g++", "-O2", "-std=c++17", "-w", "-o", exe, path], check=True)
        return [exe]
    if ext == ".java":
        out = os.path.join(build, "java_" + base)
        os.makedirs(out, exist_ok=True)
        subprocess.run(["javac", "-d", out, path], check=True,
                       stderr=subprocess.DEVNULL)
        return ["java", "-Xss64m", "-cp", out, base]
    if ext == ".py":
        return [sys.executable, path]
    raise ValueError(path)


def run(cmd, inp_path, limit):
    with open(inp_path, "rb") as f:
        start = time.perf_counter()
        try:
            p = subprocess.run(cmd, stdin=f, capture_output=True, timeout=limit)
        except subprocess.TimeoutExpired:
            return "TLE", limit
        elapsed = time.perf_counter() - start
    if p.returncode != 0:
        return "RTE", elapsed
    return p.stdout.decode().strip(), elapsed


tests = sorted(glob.glob(os.path.join(ROOT, "data", "sample", "*.in")) +
               glob.glob(os.path.join(ROOT, "data", "secret", "*.in")))
subs = []
for folder in ("accepted", "wrong_answer", "time_limit_exceeded", "run_time_error"):
    for p in sorted(glob.glob(os.path.join(ROOT, "submissions", folder, "*"))):
        if p.endswith((".cpp", ".java", ".py")):
            subs.append((folder, p))

expected = {t: open(t[:-3] + ".ans").read().strip() for t in tests}
results = {}
problems = []
for folder, path in subs:
    key = folder + "/" + os.path.basename(path)
    try:
        cmd = prepare(path)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("%-52s SKIPPED (compiler for %s not found)" % (key, os.path.splitext(path)[1]))
        continue
    res = {}
    for t in tests:
        out, secs = run(cmd, t, TL)
        if out in ("TLE", "RTE"):
            verdict = out
        else:
            verdict = "AC" if out == expected[t] else "WA"
        res[os.path.relpath(t, os.path.join(ROOT, "data"))] = (verdict, round(secs, 3))
    results[key] = res
    verdicts = [v for v, _ in res.values()]
    summary = {v: verdicts.count(v) for v in ("AC", "WA", "TLE", "RTE")}
    worst = max(s for _, s in res.values())
    print("%-52s AC=%2d WA=%2d TLE=%2d RTE=%2d  slowest=%.2fs" % (
        key, summary["AC"], summary["WA"], summary["TLE"], summary["RTE"], worst))
    ok = {
        "accepted": summary["WA"] + summary["TLE"] + summary["RTE"] == 0,
        "wrong_answer": summary["WA"] > 0 and summary["TLE"] + summary["RTE"] == 0,
        "time_limit_exceeded": summary["TLE"] > 0 and summary["WA"] == 0,
        "run_time_error": summary["RTE"] > 0 and summary["WA"] == 0,
    }[folder]
    if not ok:
        problems.append(key)

print()
if problems:
    print("FOLDER / VERDICT MISMATCH:", problems)
else:
    print("All submissions behave as their folder says (limit %.1fs)." % TL)

if JSON_OUT:
    with open(JSON_OUT, "w") as f:
        json.dump({"tl": TL, "results": results}, f, indent=1)
sys.exit(1 if problems else 0)
