'这是一个演示模块'
# print('模块级别语句')
def foo():
    print('模块级别函数')
if __name__ == '__main__':
    print('模块级别语句')
    foo()
    print('这是最小的空模块')