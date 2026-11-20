Input validator for "Awkward-Free Photo"
validator.py reads the input from stdin and exits with 42 if it matches the statement exactly, 43 otherwise.

It checks: line 1 = n (2 <= n <= 100000, no sign / leading zeros); line 2 = n integers separated by single spaces,
1 <= a[i] <= n and a[i] != i; exactly two lines, each ending in '\n', nothing afterwards (no tabs, CRLF, blank lines, trailing spaces).

