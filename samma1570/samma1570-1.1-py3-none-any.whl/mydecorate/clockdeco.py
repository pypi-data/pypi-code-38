#   @author: 马朝威 1570858572@qq.com
#   @time: 2019-02-24 21:02
import datetime
import functools


def clockdeco(func):
    @functools.wraps(func)
    def wrapper(*args):
        start = datetime.datetime.now()
        result = func(*args)
        end = datetime.datetime.now()
        print('func : {} cunsumes {} second'.format(func.__name__, (end-start).seconds))
        return result
    return wrapper


@clockdeco
def sayhello():
    print("hello world!!")













