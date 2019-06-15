# -*- coding: utf-8 -*-

from source.trigger.jira import Jira


def test_jira():
    jira = Jira ()
    assert (jira is not None)
