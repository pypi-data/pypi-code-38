#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from cherrypy import tools
import requests
from pacifica.policy.config import get_config


# pylint: disable=too-few-public-methods
class TransactionSearch(object):
    """Retrieves a set of transactions for a given keyword set."""

    exposed = True

    @staticmethod
    def _get_transactions_for_keywords(kwargs, option=None):
        """Return a list with all the projects involving this user."""
        md_url = '{0}/transactioninfo/search/{1}'.format(
            get_config().get('metadata', 'endpoint_url'), option)
        response = requests.get(url=md_url, params=kwargs)

        return response.json()

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    def GET(option=None, **kwargs):
        """CherryPy GET method."""
        return TransactionSearch._get_transactions_for_keywords(kwargs, option)
# pylint: enable=too-few-public-methods
