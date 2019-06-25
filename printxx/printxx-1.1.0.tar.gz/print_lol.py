def print_lolx(v_list):
    for v in v_list:
        if isinstance(v, list):
            print_lolx(v)
        else:
            print(v)


"""这是一个函数"""


# 特定函数2
def print_lolxx(v_list, indent=False, level=0):
    for v in v_list:
        if isinstance(v, list):
            print_lolxx(v, indent, level + 1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end='')
            print(v)
