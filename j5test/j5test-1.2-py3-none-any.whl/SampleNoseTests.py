# -*- coding: utf-8 -*-

"""Helper module for nose tests helper"""

def test_must_pass():
    """check normal tests pass"""
    assert True

def must_not_test():
    """check we're not testing tests that don't start with test (our normal config)"""
    assert False


