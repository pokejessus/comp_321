"""Input format validator for "Awkward-Free Photo".

Exit code 42 = input is correctly formatted, anything else = rejected
(43 is used here so a failure is distinguishable from a crash).

"""
import re
import sys

MAX_N = 10**5
# At most 6 digits (100000 is the largest legal value), so tokens can never be arbitrarily long.
INT = re.compile(rb"^(0|[1-9][0-9]{0,5})$")


def fail(msg):
    sys.stderr.write("INVALID: " + msg + "\n")
    sys.exit(43)


def main():
    data = sys.stdin.buffer.read()

    if not data.endswith(b"\n"):
        fail("file must end with a newline")
    lines = data.split(b"\n")
    # data ends with '\n', so the last element after split is the empty string
    if len(lines) != 3 or lines[2] != b"":
        fail("input must consist of exactly two lines")
    first, second = lines[0], lines[1]

    if not INT.match(first):
        fail("first line must be a single integer without spaces or leading zeros")
    n = int(first)
    if not (2 <= n <= MAX_N):
        fail("n out of range [2, 10^5]")

    tokens = second.split(b" ")
    if len(tokens) != n:
        fail("second line must contain exactly n integers separated by single spaces")
    for i, tok in enumerate(tokens, start=1):
        if not INT.match(tok):
            fail("a_%d is not a valid integer (empty token, extra space, sign or leading zero?)" % i)
        v = int(tok)
        if not (1 <= v <= n):
            fail("a_%d = %d is outside [1, n]" % (i, v))
        if v == i:
            fail("a_%d = %d: a guest cannot give a gift to himself/herself" % (i, i))

    sys.exit(42)


main()