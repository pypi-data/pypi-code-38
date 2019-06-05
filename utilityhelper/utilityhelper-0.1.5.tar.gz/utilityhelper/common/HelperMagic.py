#coding:utf-8
from __future__ import (print_function, unicode_literals)

def wrapper_round_n_float(radix):
    def flyable_to_return(cls):
        def r(self, num):
            return round(num, radix)
        cls.r = r
        return cls
    return flyable_to_return

@wrapper_round_n_float(5)
class R(float):
    pass


class Round2Float(float):
    """派生不可变类型
    关于”__new__”有一个重要的用途就是用来派生不可变类型。
    例如，Python中float是不可变类型，如果想要从float中派生一个子类，就要实现”__new__”方法："""
    def __new__(cls, num):
        num = round(num, 2)
        return super(Round2Float, cls).__new__(cls, num)
        # return float.__new__(Round2Float, num)


if __name__ == "__main__":
    f = Round2Float(4.14159)
    print(f)

    rr = R()
    # print rr.r(5.1111111)