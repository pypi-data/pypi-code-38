# coding: utf-8
""" Base module with all core functionalities needed to help us in the building process of
instances
"""
import locale

try:
    locale.setlocale(locale.LC_ALL, '')
    CHARSET = locale.getlocale(locale.LC_CTYPE)[1]
except locale.Error:
    CHARSET = None
if CHARSET is None:
    CHARSET = 'ascii'
