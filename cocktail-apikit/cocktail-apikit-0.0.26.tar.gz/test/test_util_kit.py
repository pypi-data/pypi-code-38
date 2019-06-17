#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Creation: 4/17/19 7:31 PM
@Author: liang
@File: test_util_kit.py
"""
import pytest

from cocktail_apikit.utils_kit import dict_attr


@pytest.fixture
def dict_obj():
    return {
        'type': 'book',
        'author': {
            'name': 'test',
            'email': 'test@mail.com',
            'meta': {
                'age': 10
            }
        }
    }


def test_dict_attr(dict_obj):
    assert dict_attr(None) is None
    assert dict_attr('', None) is None
    assert dict_attr(None, None) is None

    assert dict_attr(dict_obj, 'name') is None
    assert dict_attr(dict_obj, 'type') == 'book'
    assert isinstance(dict_attr(dict_obj, 'author'), dict)

    assert dict_attr(dict_obj, 'author.nothing') is None
    assert dict_attr(dict_obj, 'author.name') == 'test'
    assert dict_attr(dict_obj, 'author.email') == 'test@mail.com'

    assert dict_attr(dict_obj, 'author.meta.age') == 10
