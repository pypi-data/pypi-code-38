#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/30
from unittest import TestCase

from libs.utils import Singleton, str_placeholder_replace


class TestSingletonClass(Singleton):
    def __init__(self):
        print('123+++')


class TestSingleton(TestCase):

    def test_instance(self):
        a = TestSingletonClass.instance()
        b = TestSingletonClass.instance()
        print(f'是否是同一个对象{a == b}')


class TestStrPlaceholderReplace(TestCase):

    def test_str_placeholder_replace(self):
        # value = '${${b}}'
        # value = 'a${b}c${d}_${d${e}}_${${f}}abcd'
        value = '''
        }${a}{
        'a': 'av',
         'b': '${b}',
         'c': [1,2,${f}]
         }}}'''
        value_map = {
            'b': 'b',
            'd': 'd',
            'e': 'e',
            'de': '#',
            'f': 'de'
        }
        result = str_placeholder_replace('${', '}', value, value_map)
        print(result)
