# -*- coding: utf-8 -*-

from mailtrigger.argument import Argument


def test_argument():
    argument = Argument()
    assert (argument is not None)
