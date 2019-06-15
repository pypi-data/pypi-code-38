# -*- coding: utf-8 -*-

from source.trigger.jenkins import Jenkins


def test_jenkins():
    jenkins = Jenkins()
    assert (jenkins is not None)
