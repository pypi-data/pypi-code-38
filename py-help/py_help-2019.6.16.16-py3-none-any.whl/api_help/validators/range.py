# -*- coding: utf-8 -*-

from marshmallow.validate import (
    URL, Email, Range, Length, Equal, Regexp,
    Predicate, NoneOf, OneOf, ContainsOnly
)
from ..validator import debug, info, warn, error


class RangeValid(Range):
    def __init__(self, param_str):
        if '-' in param_str:
            param_arr = param_str.split('-')
        elif '..' in param_str:
            param_arr = param_str.split('..')
        else:
            error("range的输入需要用-号隔开:{}".format(param_str))
            param_arr = ['0', '65535']
        if len(param_arr[0]) == 0:
            min_v = None
        else:
            min_v = float(param_arr[0])
        if len(param_arr[1]) == 0:
            max_v = None
        else:
            max_v = float(param_arr[1])
        super(RangeValid, self).__init__(min_v, max_v)
