def main():
    n = int(input())
    a = [x - 1 for x in map(int, input().split())]
    selected = [False] * n
    has_selected_giver = [False] * n # has_selected_giver[i]: guest in photo gives gift to guest i

    for guest in range(n):
        receiver = a[guest]

        # pick guest if guest does not give to someone in the photo and if nobody in the photo gives to this guest 
        if not selected[receiver] and not has_selected_giver[guest]:
            selected[guest] = True
            has_selected_giver[receiver] = True

    print(sum(selected))

if __name__ == "__main__":
    main()