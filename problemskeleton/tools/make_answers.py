#!/usr/bin/env python3
"""Write the .ans files by running the accepted solution on every .in file.
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUTE_MAX_N = 22


def run(cmd, path, timeout=120):
    with open(path, "rb") as f:
        r = subprocess.run(cmd, stdin=f, capture_output=True, timeout=timeout)
    if r.returncode != 0:
        raise SystemExit("%s failed on %s" % (cmd, path))
    return r.stdout.decode().strip()


def main():
    py = os.path.join(ROOT, "submissions", "accepted", "solution.py")
    brute = os.path.join(ROOT, "submissions", "run_time_error", "brute_force.py")
    if shutil.which("g++"):
        exe = os.path.join(tempfile.mkdtemp(prefix="awkward_ans_"), "solution")
        subprocess.run(["g++", "-O2", "-std=c++17", "-w", "-o", exe,
                        os.path.join(ROOT, "submissions", "accepted", "solution.cpp")], check=True)
        main_cmd, main_name = [exe], "solution.cpp"
    else:
        print("g++ not found: using solution.py as the main solution (no C++ cross-check)")
        main_cmd, main_name = [sys.executable, py], "solution.py"
    inputs = sorted(glob.glob(os.path.join(ROOT, "data", "*", "*.in")))
    if not inputs:
        raise SystemExit("no .in files found: run test_case_generator/generator.py first")
    checked_brute = 0
    for path in inputs:
        ans = run(main_cmd, path)
        if main_name == "solution.cpp" and run([sys.executable, py], path) != ans:
            raise SystemExit("solution.cpp and solution.py disagree on %s" % path)
        with open(path) as f:
            n = int(f.readline())
        if n <= BRUTE_MAX_N:
            if run([sys.executable, brute], path) != ans:
                raise SystemExit("brute force disagrees on %s" % path)
            checked_brute += 1
        with open(path[:-3] + ".ans", "w") as f:
            f.write(ans + "\n")
    print("wrote %d .ans files using %s; checked against the brute force on the %d inputs with n <= %d"
          % (len(inputs), main_name, checked_brute, BRUTE_MAX_N))


if __name__ == "__main__":
    main()