#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from cherrypy import tools, HTTPError
import requests
from pacifica.policy.config import get_config
from pacifica.policy.status.base import QueryBase


# pylint: disable=too-few-public-methods
class UserSearch(QueryBase):
    """Retrieves a set of projects for a given keyword set."""

    exposed = True

    @staticmethod
    def _get_users_for_keywords(kwargs, search_terms=None, option=None):
        """Return a list with all the projects involving this user."""
        md_url = '{0}/userinfo/search/{1}'.format(
            get_config().get('metadata', 'endpoint_url'), search_terms)
        if option is not None:
            md_url += '/{0}'.format(option)
        response = requests.get(url=md_url, params=kwargs)
        retval = response.json()
        if response.status_code == 200:
            return retval
        else:
            raise HTTPError(response.status_code)

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @tools.json_out()
    def GET(self, search_terms=None, option=None, **kwargs):
        """CherryPy GET method."""
        return self._get_users_for_keywords(kwargs, search_terms, option)
# pylint: enable=too-few-public-methods
