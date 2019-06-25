def print_lolx(v_list):
    for v in v_list:
        if isinstance(v, list):
            print_lolx(v)
        else:
            print(v)


"""这是一个函数"""
# 特定函数
