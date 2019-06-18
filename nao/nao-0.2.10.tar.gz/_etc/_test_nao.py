# -*- coding: utf-8 -*-

import doctest
import unittest
import pytest

import nao
import babel

def test_nao():
    assert len('er') = 2


test_str = """
en:
    -   _alpha: a
        _prod: b 
        _test: c 
    -   _alpha: e
        _prod: f 
        exert: g  # this could be a deafult
    -   _prod:
        _test:

hu:
    _neme: 1
    vele: 2
    rola: 34

zz_QQ:  # not a language -> default value

"""

strip = nao.strip_string

def test_syntax():

    conf = nao.load(strip("""
        _alpha:
            en: This is a deafult value
            hu: this is also
            hu:
                _prod: 23 # never show up
            en_GB: shiite

        _prod:
            overlayed on default for every language
            en:
                what?
            hu:
                mi?

        _test: 23

        en:
            _prod: make it
        """))

    # defaults to alpha, en
    assert nao.yaml == strip("""
        This is a default value
        """)
    
    # check prod, en
    assert nao['prod'] == strip("""
        make it
        """)

    assert nao['']

    # conf is a multilingual and multivalue config

    assert nao.auto_babel == True
    assert nao.filters == {
        'babel': BabelFilter(),
        'simple': SimpleFilter(),

    }

    # simplefilter.force_order
    # simplefilter.load_style overlay/atomic (check anyconfig)
        # filter.load_style


