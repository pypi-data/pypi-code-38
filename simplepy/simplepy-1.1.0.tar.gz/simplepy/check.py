# -*- coding: utf-8 -*-


def type_check(name, expect_type=None):
    @property
    def check(self):
        return name

    if name == 'num':

        @check.setter
        def check(self, value):
            if not isinstance(value, expect_type):
                raise TypeError('{} must be a {}.'.format(value, expect_type))

            if value < 1:
                raise TypeError('You input is {}, must >=1.'.format(value))
    elif name == 'mode':
        @check.setter
        def check(self, value):
            if value not in ['R', 'S', 'D', 'T', 'F'] or not isinstance(value, str):
                raise TypeError('Please input correct mode.')
            setattr(self, name, 'F')

    elif name == 'is_upper':
        @check.setter
        def check(self, value):
            if value not in [0, 1, 2]:
                raise TypeError('Please input correct is_upper.')

            setattr(self, name, 0)

    return check
