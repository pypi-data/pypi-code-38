#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from pacifica.policy.status.project.by_user import ProjectUserSearch
from pacifica.policy.status.project.search import ProjectKeywordSearch
from pacifica.policy.status.project.lookup import ProjectLookup


# pylint: disable=too-few-public-methods
class ProjectQuery(object):
    """CherryPy root object class."""

    exposed = False

    def __init__(self):
        """Create local objects for sub tree items."""
        self.by_user_id = ProjectUserSearch()
        self.search = ProjectKeywordSearch()
        self.by_project_id = ProjectLookup()
# pylint: enable=too-few-public-methods
