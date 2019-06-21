#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from pacifica.policy.status.user.search import UserSearch
from pacifica.policy.status.user.lookup import UserLookup


# pylint: disable=too-few-public-methods
class UserQuery(object):
    """CherryPy root object class."""

    exposed = True

    def __init__(self):
        """Create local objects for sub tree items."""
        self.search = UserSearch()
        self.by_id = UserLookup()
# pylint: enable=too-few-public-methods
