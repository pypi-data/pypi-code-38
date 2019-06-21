#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from cherrypy import tools
import requests
from pacifica.policy.validation import validate_user
from pacifica.policy.config import get_config


# pylint: disable=too-few-public-methods
class UserLookup(object):
    """Retrieves info for the specified user."""

    exposed = True

    @staticmethod
    def _get_user_info(user_id):
        """Return detailed info about a given user."""
        lookup_url = '{0}/userinfo/by_id/{1}'.format(
            get_config().get('metadata', 'endpoint_url'), user_id
        )
        return requests.get(url=lookup_url).json()

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @validate_user()
    def GET(user_id=None):
        """CherryPy GET method."""
        return UserLookup._get_user_info(user_id)
# pylint: enable=too-few-public-methods
