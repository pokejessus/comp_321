import sys

sys.setrecursionlimit(10**6)

def backtrack(u, n, a, selected):
    # base case: all guests decided
    if u == n:
        # check if person guest is giving gift to is picked, if yes not an independent set
        for guest in selected:
            receiver = a[guest]

            if receiver in selected:
                return 0
        
        return len(selected)

    best = backtrack(u + 1, n, a, selected) # choice 1: skip guest u

    selected.append(u) # choice 2: pick guest u
    best = max(best, backtrack(u + 1, n, a, selected))

    selected.pop()

    return best

def main():
    n = int(input())
    a = [x - 1 for x in map(int, input().split())]
    selected = []

    answer = backtrack(0, n, a, selected)

    print(answer)


if __name__ == "__main__":
    main()