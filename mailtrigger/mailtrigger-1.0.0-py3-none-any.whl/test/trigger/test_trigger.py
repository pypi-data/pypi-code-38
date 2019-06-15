# -*- coding: utf-8 -*-

from source.trigger.trigger import Trigger


def test_trigger():
    trigger = Trigger()
    assert (trigger is not None)
