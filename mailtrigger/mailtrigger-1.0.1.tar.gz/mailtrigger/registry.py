# -*- coding: utf-8 -*-

from .trigger.gerrit import Gerrit
from .trigger.jenkins import Jenkins
from .trigger.jira import Jira

REGISTRY = [
    {
        'class': Gerrit,
        'name': Gerrit.__name__.lower()
    },
    {
        'class': Jenkins,
        'name': Jenkins.__name__.lower()
    },
    {
        'class': Jira,
        'name': Jira.__name__.lower()
    }
]
