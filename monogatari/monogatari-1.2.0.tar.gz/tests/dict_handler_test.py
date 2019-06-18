# -*- coding: utf-8 -*-
# Copyright 2019 Bruno Toshio Sugano <brunotoshio@gmail.com>
import os

import pytest

from monogatari.dict_handler import DictHandler


@pytest.fixture
def handler():
    test_dir = os.path.dirname(__file__)
    return DictHandler(f'{test_dir}/testdic.dic')


def test_parse_categories(handler):
    assert all(k in handler._categories for k in ['01', '02'])
    assert all(v in handler._categories.values() for v in ['HarmVirtue', 'HarmVice'])


def test_parse_normal_keys(handler):
    assert all(k in handler._normal_dict for k in ['守る', '親善', '害'])
    assert all(k not in handler._normal_dict for k in ['安全*', '友情*', '損害*'])


def test_parse_wildcard_keys(handler):
    assert all(k in handler._wildcard_dict for k in ['安全*', '友情*', '損害*'])
    assert all(k not in handler._wildcard_dict for k in ['守る', '親善', '害'])


def test_wildcard_search_found(handler):
    assert handler._wildcard_search('友情*') == ['HarmVirtue', 'HarmVice']


def test_wildcard_search_not_found(handler):
    assert handler._wildcard_search('守る*') == []


def test_search_found(handler):
    assert handler.search('守る') == ['HarmVirtue']
    assert handler.search('友情*') == ['HarmVirtue', 'HarmVice']


def test_search_not_found(handler):
    assert handler.search('友情') == []
    assert handler.search('守る*') == []


def test_categories(handler):
    assert handler.categories() == ['HarmVirtue', 'HarmVice']
