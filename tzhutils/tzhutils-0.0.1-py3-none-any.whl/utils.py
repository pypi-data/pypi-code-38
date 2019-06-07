from functools import wraps
import requests
from lxml import etree
import time
import sys
import progressbar


##关于时间函数
t = lambda : time.time()
now = lambda : time.ctime()
######################################################################################################

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
}


#wrap functions for try and exception structure
def try_wrap(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        try:
            print('='*100)
            print(func.__name__ + " function was called.\n")
            return func(*args, **kwargs)
        except Exception as e:
            print('!#'*50)
            print('errors in function: ', func.__name__)
            print(e)
            print('!#'*50)
        finally:
            print('='*100)
    return with_logging



'''
example:

@try_wrap
def test():
    print('this is a test')
    a = 1 / 0
    print(a)
    
test()
'''
######################################################################################################

def wrap_time(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        try:
            print('='*100)
            print('start at : ', now(), '\n')
            t0 = t()
            print(func.__name__ + " function was called successfully.\n")
            return func(*args, **kwargs)
        except Exception as e:
            print('!#'*50)
            print('errors in function: ', func.__name__)
            print(e)
            print('\n\n')
        finally:
            t1 = t()
            print()
            print('stop at : ', now())
            print('total cost {}s'.format(t1 - t0))
            print("Function ", sys._getframe().f_code.co_name, "ended.\n")
            print('='*100)
    return with_logging

##example:
# @wrap_time
# def test():
#     print('this is test '* 10)
#     for i in range(100000000):
#         pass
# test()
######################################################################################################


@try_wrap
def write_into_file(filename, read_or_write, contents):
    with open(filename, read_or_write) as f:
        f.write(contents + '\n')
        print('successfully writing file.')

#write_into_file('test.txt', 'a', 'this is test\n and test')


@try_wrap
def read_file(filename, read_or_write='r'):
    with open(filename, read_or_write) as f:
        contents = f.readlines()
        print('successfully reading file.')
        return contents


@try_wrap
def get_html_content(url):
    res = requests.get(url, headers=headers)
    res.encoding = 'gbk'
    res = res.text
    # print(res)
    return res


@try_wrap
def parse_html(response, parse_format):
    html = etree.HTML(response)
    find_attr = html.xpath(parse_format)
    print(find_attr, '\n')
    return find_attr

##进度条初始化以及魔法糖函数建立,使用此函数必须要提前定义数量n
def bar_wrap(func):
    @wraps(func)
    def bar_wrap_inner(n):
        print('begin time bar wrap: ')
        bar = progressbar.ProgressBar()
        for i in bar(range(n)):
            time.sleep(0)
        return func(n)
    return bar_wrap_inner

#example of test bar wrap:
# @bar_wrap
# def bar_wrap_test(n):
#     print('bar wrap test over.')
# bar_wrap_test(n=100000)
##################################################################
