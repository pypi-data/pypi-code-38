# -*- coding: utf-8 -*-

from marshmallow.validate import (
    URL, Email, Range, Length, Equal, Regexp,
    Predicate, NoneOf, OneOf, ContainsOnly
)

from ..validator import debug, info, warn, error


class OneOfValid(OneOf):
    """
    单选中校验只能是备选项中的一个
    """

    def __init__(self, param_str):
        if '|' in param_str:
            param_arr = param_str.split('|')
        elif ',' in param_str:
            param_arr = param_str.split(',')
        else:
            warn("处理参数条件:{}出现异常,不能不含分隔符".format(param_str))
            param_arr = []
        super(OneOfValid, self).__init__(param_arr)
