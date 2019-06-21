#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from cherrypy import tools
import requests
from pacifica.policy.validation import validate_project
from pacifica.policy.config import get_config


# pylint: disable=too-few-public-methods
class ProjectLookup(object):
    """Retrieves details of a given project."""

    exposed = True

    @staticmethod
    def _get_projects_details(project_id=None):
        """Return a details about this project."""
        lookup_url = u'{0}/projectinfo/by_project_id/{1}'.format(
            get_config().get('metadata', 'endpoint_url'), project_id
        )
        return requests.get(url=lookup_url).json()

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @validate_project()
    def GET(project_id=None):
        """CherryPy GET method."""
        return ProjectLookup._get_projects_details(project_id)
# pylint: enable=too-few-public-methods
