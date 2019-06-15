# -*- coding: utf-8 -*-

from mailtrigger.trigger.gerrit import Gerrit


def test_gerrit():
    gerrit = Gerrit()
    assert (gerrit is not None)
