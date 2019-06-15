# -*- coding: utf-8 -*-

from mailtrigger.trigger.jira import Jira


def test_jira():
    jira = Jira ()
    assert (jira is not None)
