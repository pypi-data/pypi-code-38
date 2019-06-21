#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from cherrypy import tools
import requests
from pacifica.policy.validation import validate_transaction
from pacifica.policy.config import get_config


# pylint: disable=too-few-public-methods
class TransactionLookup(object):
    """Retrieves details of a given project."""

    exposed = True

    @staticmethod
    def _get_transaction_details(transaction_id=None):
        """Return details for the specified transaction entry."""
        md_url = '{0}/transactioninfo/by_id/{1}'.format(
            get_config().get('metadata', 'endpoint_url'), transaction_id)
        return requests.get(url=md_url).json()

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @validate_transaction()
    def GET(transaction_id=None):
        """CherryPy GET method."""
        return TransactionLookup._get_transaction_details(transaction_id)
# pylint: enable=too-few-public-methods
