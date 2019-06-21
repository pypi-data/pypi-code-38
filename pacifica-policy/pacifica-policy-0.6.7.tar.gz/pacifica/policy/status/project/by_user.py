#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from cherrypy import tools
import requests
from pacifica.policy.validation import validate_user
from pacifica.policy.config import get_config
from pacifica.policy.status.base import QueryBase


# pylint: disable=too-few-public-methods
class ProjectUserSearch(QueryBase):
    """Retrieves project list for a given user."""

    exposed = True

    @staticmethod
    def _get_projects_for_user(user_id=None):
        """Return a list with all the projects involving this user."""
        md_url = '{0}/projectinfo/by_user_id/{1}'.format(
            get_config().get('metadata', 'endpoint_url'), user_id
        )
        response = requests.get(url=md_url)

        return response.json()

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @validate_user()
    def GET(user_id=None):
        """CherryPy GET method."""
        return ProjectUserSearch._get_projects_for_user(user_id)
# pylint: enable=too-few-public-methods
