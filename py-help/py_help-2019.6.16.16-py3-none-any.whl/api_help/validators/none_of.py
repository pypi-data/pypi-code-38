# -*- coding: utf-8 -*-

from marshmallow.validate import (
    URL, Email, Range, Length, Equal, Regexp,
    Predicate, NoneOf, OneOf, ContainsOnly
)


class NoneOfValid(NoneOf):
    def __init__(self, param_str):
        param_arr = param_str.split('|')
        super(NoneOfValid, self).__init__(param_arr)
