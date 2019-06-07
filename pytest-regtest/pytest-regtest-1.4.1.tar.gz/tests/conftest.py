#! /usr/bin/env python
# encoding: utf-8
from __future__ import print_function, division, absolute_import


from pytest_regtest import register_converter_pre, register_converter_post


@register_converter_pre
def result(txt):
    return txt


@register_converter_post
def result(txt):
    return txt.upper()
