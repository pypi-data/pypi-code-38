#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Тесты модуля типов

"""

import pytest
from typing import (
    Tuple,
)


# pytest.skip('skipping {} tests'.format(__name__), allow_module_level=True)


@pytest.fixture
def constants_module():
    """Все проверяемые константы находятся в этом модуле
    """
    from tracuni import trac_uni as constants
    return constants


@pytest.fixture
def constants_spec():
    """Имена на типы ожидаемых констант
    """
    return {
        'UNKNOWN_NAME': str,
        'TRACER_SYSTEM_NAME': str,
        'CUT_LIMIT': int,
        'CUT_LINE': str,
        'TAG_ESSENTIAL_FIELD_NAMES': Tuple,
        'TAG_ESSENTIAL_BODY_NAMES': Tuple,
        'USE_TORNADO': bool,
        'PATH_IGNORE_METHODS': Tuple,
        'PATH_IGNORE_PIECE': str,
        'CONTEXT_UID_NAME': str,
        'CONTEXT_SPAN_NAME': str,
    }


#
# #
# ####################
#
#
# ####################
# # Внутренние значения
#
#
# PATH_IGNORE_METHODS = ('decorated', 'wrapper')
# PATH_IGNORE_PIECE = r'tracer_uni/'
# CONTEXT_UID_NAME = 'span_context_uid'
# CONTEXT_SPAN_NAME = 'span_context'
#
#
# #
# ####################
@pytest.fixture
def own_attributes(constants_module):
    """Проверяем только собственные идентификаторы
    """
    return [el for el in dir(constants_module) if not el.startswith('__')]


# @pytest.mark.skip(reason="no way of constants define currently testing this")
def test_const_exist(constants_module, constants_spec):
    """Все ожидаемые константы присутствуют
     и принадлежат к требуемому типу, если применимо
    """
    # noinspection PyTypeChecker
    for c_name, c_type in constants_spec.items():
        assert \
            isinstance(getattr(constants_module, c_name, None), c_type), \
            "Should have {} with type <{}> in const".format(c_name, c_type)


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_const_upper_case(own_attributes):
    """Все константы именованы в верхнем регистре
    """
    upper_cased = [el for el in own_attributes if el.isupper()]
    assert len(own_attributes) == len(upper_cased)


# @pytest.mark.skip(reason="get out of the way of the best boosted beasts")
def test_no_extra_const(own_attributes, constants_spec):
    """Нет неожиданных констант
    """
    assert len(own_attributes) <= len(constants_spec)


@pytest.fixture
def tag_essential_field_names():
    from tracuni.trac_uni import TAG_ESSENTIAL_FIELD_NAMES
    return TAG_ESSENTIAL_FIELD_NAMES


def test_tag_essential_field_names_types(tag_essential_field_names):
    for el in tag_essential_field_names:
        assert (
            type(el) == str or type(el) == tuple
        )
        if type(el) == tuple:
            for sub_el in el:
                assert type(sub_el) == str


@pytest.fixture
def tag_essential_body_names():
    from tracuni.trac_uni import TAG_ESSENTIAL_BODY_NAMES
    return TAG_ESSENTIAL_BODY_NAMES


def test_tag_essential_body_names(tag_essential_body_names):
    for el in tag_essential_body_names:
        assert (
            type(el) == str
        )


@pytest.fixture
def path_ignore_methods():
    from tracuni.trac_uni import PATH_IGNORE_METHODS
    return PATH_IGNORE_METHODS


def test_path_ignore_methods(path_ignore_methods):
    for el in path_ignore_methods:
        assert (
            type(el) == str
        )
