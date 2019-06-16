# -*- coding: utf-8 -*-
import re
from marshmallow.validate import (
    URL, Email, Range, Length, Equal, Regexp,
    Predicate, NoneOf, OneOf, ContainsOnly
)


class RegexpValid(Regexp):
    def __init__(self, param_str):
        if '/' in param_str and len(param_str.split('/')) >= 3:
            param_arr = param_str.split('/')
            flag_str = param_arr[-1].lower()
            flag = 0
            if 'i' in flag_str:
                flag = flag | re.I
            if 'x' in flag_str:
                flag = flag | re.X
            if 'u' in flag_str:
                flag = flag | re.U
            if 'm' in flag_str:
                flag = flag | re.M
            if 'l' in flag_str:
                flag = flag | re.L

            if len(param_arr) == 3:
                regexp_str = param_arr[1]
            else:
                regexp_str = ''.join(param_arr[0:-1])
            super(RegexpValid, self).__init__(regexp_str, flag)
        else:
            super(RegexpValid, self).__init__(param_str)
