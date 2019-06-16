# -*- coding: utf-8 -*-

from marshmallow.validate import (
    URL, Email, Range, Length, Equal, Regexp,
    Predicate, NoneOf, OneOf, ContainsOnly
)


class ContainsOnlyValid(ContainsOnly):
    def __init__(self, param_str):
        super(ContainsOnlyValid, self).__init__();
