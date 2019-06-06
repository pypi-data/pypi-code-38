#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Core interface for the projectinfo metadata objects to interface with CherryPy."""
from pacifica.metadata.rest.project_queries.project_lookup import ProjectLookup
from pacifica.metadata.rest.project_queries.project_term_search import ProjectTermSearch
from pacifica.metadata.rest.project_queries.project_user_search import ProjectUserSearch
from pacifica.metadata.rest.project_queries.project_has_data import ProjectHasData


# pylint: disable=too-few-public-methods
class ProjectInfoAPI(object):
    """ProjectInfo API."""

    exposed = True

    def __init__(self):
        """Create local objects for subtree items."""
        self.by_user_id = ProjectUserSearch()
        self.search = ProjectTermSearch()
        self.by_project_id = ProjectLookup()
        self.has_data = ProjectHasData()
