#!/usr/bin/env python
# coding=utf-8

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import unittest
import pytest
from unittest.mock import patch

from sopel_modules.checkiday import checkiday


class TestApi(unittest.TestCase):
    def setUp(self):
        pass

    @patch('sopel_modules.checkiday.requests.get')
    def test_api_request_returns_dict(self, mg):
        mg.return_value.json.return_value = {'error': 'none'}

        api_response = checkiday.request_api()
        assert api_response == {'error': 'none'}

    @patch('sopel_modules.checkiday.requests.get')
    def test_api_request_error_returns_exception(self, mg):
        mg.return_value.json.return_value = {'error': 'not none'}

        with pytest.raises(ValueError,
                           match='Api call returned error: not none'):
            checkiday.request_api()


def test_return_list_from_json():
    j = {'holidays': [{'name': 'test1'}, {'name': 'test2'}]}
    day_list = checkiday.get_days_from_json(j)

    assert day_list == ['test1', 'test2']


def test_apply_colours():
    cdays = checkiday.apply_colours(['abc', 'def', 'ghi'], [1, 2])

    assert cdays == ['\x0301abc\x03', '\x0302def\x03', '\x0301ghi\x03']


#  def test_num_ranges():
#      nr = checkiday.num_ranges(840, 400)
#      assert list(nr) == [0, 400, 800, 840]


#  def test_split_messages():
#      days = ['a'] * 140
#      output_lines = checkiday.split_msg(days)

#      assert [len(i) for i in output_lines] == [397, 16]

def test_split_messages():
    days = ['test 1', 'test 2'] * 26
    output_lines = checkiday.split_msg(days)

    assert output_lines[-1] == 'test 1, test 2'
