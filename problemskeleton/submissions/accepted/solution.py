import sys

def solve():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = [int(x) - 1 for x in data[1:n + 1]]

    indeg = [0] * n
    for v in a:
        indeg[v] += 1

    dp0 = [0] * n   # vertex not taken
    dp1 = [1] * n   # vertex taken

    # Peel the trees (leaves first)
    stack = [i for i in range(n) if indeg[i] == 0]
    while stack:
        v = stack.pop()
        u = a[v]
        d0, d1 = dp0[v], dp1[v]
        dp0[u] += d0 if d0 > d1 else d1
        dp1[u] += d0
        indeg[u] -= 1
        if indeg[u] == 0:
            stack.append(u)

    NEG = -10**9
    visited = [False] * n
    ans = 0

    for s in range(n):
        if indeg[s] > 0 and not visited[s]:
            # collect the cycle
            cyc = []
            v = s
            while not visited[v]:
                visited[v] = True
                cyc.append(v)
                v = a[v]

            best = 0
            for first_taken in (False, True):
                c0 = cyc[0]
                if first_taken:
                    p0, p1 = NEG, dp1[c0]
                else:
                    p0, p1 = dp0[c0], NEG
                for i in range(1, len(cyc)):
                    c = cyc[i]
                    n0 = (p0 if p0 > p1 else p1) + dp0[c]
                    n1 = p0 + dp1[c]
                    p0, p1 = n0, n1
                res = p0 if first_taken else (p0 if p0 > p1 else p1)
                if res > best:
                    best = res
            ans += best

    print(ans)

if __name__ == "__main__":
    solve()