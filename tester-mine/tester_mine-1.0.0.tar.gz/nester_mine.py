def print_u(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_u(each_item)
        else:
            print(each_item)


def addition(a, b):
    return a + b
