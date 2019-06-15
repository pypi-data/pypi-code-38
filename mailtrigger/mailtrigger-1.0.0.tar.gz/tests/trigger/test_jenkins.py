# -*- coding: utf-8 -*-

from mailtrigger.trigger.jenkins import Jenkins


def test_jenkins():
    jenkins = Jenkins()
    assert (jenkins is not None)
