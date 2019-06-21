'''此模块包含了学习《Head First Python》所写的示例代码
   可能一些函数可以复用
                               laoliu'''
def print_lol(the_list):
    '''使用递归函数实现复杂列表数据打印的函数'''
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
