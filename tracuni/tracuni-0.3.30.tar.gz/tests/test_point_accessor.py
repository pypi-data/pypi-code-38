#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тесты модуля доступа к вызываемой точке

"""

import pytest


# pytest.skip('skipping {} tests'.format(__name__), allow_module_level=True)


###############################################################################
# Настройки трассера и сервиса сбора метрик


@pytest.fixture
def point_accessor_type():
    """
    """
    # mocker.patch('trac_uni.const.UNKNOWN_NAME', unknown_name)
    from tracuni.trac_uni import PointAccessor
    return PointAccessor


def test_class_exist(point_accessor_type):
    assert hasattr(point_accessor_type({}), 'point_context')
