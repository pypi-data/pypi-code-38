# -*- coding: utf-8 -*-

__author__ = 'Daniel Scheffler'


def is_number(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
