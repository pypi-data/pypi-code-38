# Created by Q-ays.
# whosqays@gmail.com

from wisdoms.commons import revert, codes
from inspect import ismethod, isfunction
import traceback


def joint_base2(url1, url2):
    url1 = str(url1)
    url2 = str(url2)
    if url1.endswith('/') and not url2.startswith('/'):
        return url1 + url2
    elif not url1.endswith('/') and url2.startswith('/'):
        return url1 + url2
    elif url1.endswith('/') and url2.startswith('/'):
        return url1 + url2[1:]
    else:
        return url1 + '/' + url2


def joint4path(*args):
    """
    连接n个路径
    :param args:a,b,c,d
    :return: a/b/c/d
    """
    url1 = args[0]

    length1 = len(args)
    if length1 > 1:
        for i in range(1, length1):
            url1 = joint_base2(url1, args[i])

    return url1


def o2d(obj):
    """
    把对象(支持单个对象、list、set)转换成字典
    :param obj: obj, list, set
    :return:
    """
    is_list = isinstance(obj, list)
    is_set = isinstance(obj, set)

    if is_list or is_set:
        obj_arr = []
        for o in obj:
            # 把Object对象转换成Dict对象
            if o:
                dict1 = {}
                dict1.update(o.__dict__)
                obj_arr.append(dict1)
        return obj_arr
    else:
        dict1 = {}
        dict1.update(obj.__dict__)
        return dict1


def func_exception(code=codes.ERROR):
    """
    捕获方法异常装饰器
    :param code:
    :return:
    """

    def func_wrapper(func):
        def catch(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # print('~~~~~~~~~~~~~~~~~~~~ ', e, ' ~~~~~~~~~~~~~~~~~~~~~~~~~')
                traceback.print_exc()

                return revert(code, e)

        return catch

    return func_wrapper


def dec4method(xpt):
    """
    类装饰器，作用于实例下面的所有方法。
    注意如果是静态方法，用类名调用方法名会报错，必须用实例调用方法名。
    该装饰器直接作用于子类。
    :param xpt: 方法装饰器
    :return:
    """

    def cls_wrapper(cls):

        class Wrapper(object):

            def __init__(self, *args, **kwargs):
                self.wrapper = cls(*args, **kwargs)

            def __getattr__(self, item):

                res = getattr(self.wrapper, item)

                if ismethod(res) or isfunction(res):

                    @xpt
                    def func(*args, **kwargs):
                        return res(*args, **kwargs)

                    return func
                else:
                    return res

        return Wrapper

    return cls_wrapper


def cls_exception(xpt):
    """
    类装饰器，捕获类生成实例方法下面所有异常。
    注意如果是静态方法，用类名调用方法名会报错，必须用实例调用方法名。
    该装饰器直接作用于子类。
    :param xpt: 方法装饰器
    :return:
    """

    return dec4method(xpt)


xpt_func = func_exception()
xpt_cls = cls_exception(xpt_func)
