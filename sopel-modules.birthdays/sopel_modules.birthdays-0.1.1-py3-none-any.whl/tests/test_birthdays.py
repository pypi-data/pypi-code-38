#!/usr/bin/env python
# coding=utf-8

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import unittest
import pytest

from sopel_modules.birthdays import birthdays


def test_get_names():
    j = {
        'data': {
            'Births': [
                {'text': 'person1, description'}
            ],
            'Deaths': [
                {'text': 'person2, description'}
            ]
        }
    }

    assert birthdays.get_births(j) == ['person1']
    assert birthdays.get_deaths(j) == ['person2']


def test_apply_colours():
    cdays = birthdays.apply_colours(['abc', 'def', 'ghi'], [1, 2])

    assert cdays == ['\x0301abc\x03', '\x0302def\x03', '\x0301ghi\x03']


def test_split_messages():
    days = ['test 1', 'test 2'] * 26
    output_lines = birthdays.split_msg(days)

    assert output_lines[-1] == 'test 1, test 2'
