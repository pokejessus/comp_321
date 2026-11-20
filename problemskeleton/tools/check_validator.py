#!/usr/bin/env python3
"""Check the input validator: every .in file must be accepted (exit 42) and a
collection of deliberately malformed inputs must be rejected (exit != 42).
"""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATOR = [sys.executable, os.path.join(ROOT, "input_format_validators", "validator.py")]


def code(data):
    return subprocess.run(VALIDATOR, input=data, capture_output=True).returncode


bad = 0
files = sorted(glob.glob(os.path.join(ROOT, "data", "*", "*.in")))
for f in files:
    c = code(open(f, "rb").read())
    if c != 42:
        print("REJECTED GOOD FILE", f, c)
        bad += 1
print("good files accepted: %d / %d" % (len(files) - bad, len(files)))

N_MAX = 10 ** 5
cyc = lambda n: " ".join(str(i % n + 1) for i in range(1, n + 1))
MALFORMED = {
    "n too small (1)": b"1\n1\n",
    "n = 0": b"0\n\n",
    "n too big": ("%d\n%s\n" % (N_MAX + 1, cyc(N_MAX + 1))).encode(),
    "negative n": b"-3\n2 3 1\n",
    "n with leading zero": b"03\n2 3 1\n",
    "n with plus sign": b"+3\n2 3 1\n",
    "n not a number": b"abc\n2 3 1\n",
    "n with trailing space": b"3 \n2 3 1\n",
    "too few numbers": b"3\n2 3\n",
    "too many numbers": b"3\n2 3 1 2\n",
    "a_i = i (self gift)": b"3\n1 3 1\n",
    "a_i = 0": b"3\n0 3 1\n",
    "a_i > n": b"3\n2 4 1\n",
    "a_i negative": b"3\n2 -3 1\n",
    "a_i leading zero": b"3\n02 3 1\n",
    "a_i non-numeric": b"3\n2 x 1\n",
    "a_i float": b"3\n2 3.0 1\n",
    "double space": b"3\n2  3 1\n",
    "leading space": b"3\n 2 3 1\n",
    "trailing space": b"3\n2 3 1 \n",
    "tab separator": b"3\n2\t3 1\n",
    "missing final newline": b"3\n2 3 1",
    "extra blank line at end": b"3\n2 3 1\n\n",
    "extra data line": b"3\n2 3 1\n1\n",
    "numbers on separate lines": b"3\n2\n3\n1\n",
    "windows line endings": b"3\r\n2 3 1\r\n",
    "empty file": b"",
    "only n": b"3\n",
    "blank second line": b"3\n\n",
}
for name, data in MALFORMED.items():
    c = code(data)
    flag = "ok " if c != 42 else "BAD"
    if c == 42:
        bad += 1
    print("  [%s] malformed input rejected (exit %3d): %s" % (flag, c, name))

# a few boundary inputs that MUST be accepted
GOOD = {
    "n = 2": b"2\n2 1\n",
    "n = 10^5 pure cycle": ("%d\n%s\n" % (N_MAX, cyc(N_MAX))).encode(),
    "repeated values allowed": b"4\n2 1 1 1\n",
}
for name, data in GOOD.items():
    c = code(data)
    flag = "ok " if c == 42 else "BAD"
    if c != 42:
        bad += 1
    print("  [%s] boundary input accepted  (exit %3d): %s" % (flag, c, name))

print("\nVALIDATOR CHECK", "PASSED" if bad == 0 else "FAILED (%d problems)" % bad)
sys.exit(0 if bad == 0 else 1)
