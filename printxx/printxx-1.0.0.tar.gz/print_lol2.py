def print_lolx2(list_in, level):
    for v in list_in:
        if isinstance(v, list):
            print_lolx2(v, level + 1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(v)
