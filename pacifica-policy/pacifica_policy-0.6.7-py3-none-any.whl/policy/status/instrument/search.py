#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from json import loads
from cherrypy import tools, HTTPError
import requests
from pacifica.policy.config import get_config
from pacifica.policy.status.base import QueryBase


# pylint: disable=too-few-public-methods
class InstrumentKeywordSearch(QueryBase):
    """Retrieves a set of projects for a given keyword set."""

    exposed = True

    def _get_instruments_for_keywords(self, user_id, search_terms=''):
        """Return a list with all the instruments having this term."""
        # is_admin = self._is_admin(user_id)
        inst_list_url = '{0}/instrumentinfo/search/{1}'.format(
            get_config().get('metadata', 'endpoint_url'), search_terms
        )
        inst_query = requests.get(url=inst_list_url)
        if inst_query.status_code == 200:
            inst_response = loads(inst_query.text)
            return self._clean_up_instrument_list(inst_response, user_id)
        else:
            raise HTTPError(inst_query.status_code)

    def _clean_up_instrument_list(self, inst_response, user_id):
        """Clear out entries that done belong to this user."""
        is_admin = self._is_admin(user_id)
        output_list = []
        if not is_admin:
            inst_for_user_url = '{0}/instrumentinfo/by_user_id/{1}'.format(
                get_config().get('metadata', 'endpoint_url'), user_id
            )
            query = requests.get(url=inst_for_user_url)
            response = loads(query.text)
            output_list = InstrumentKeywordSearch._squash_output_list(
                response, inst_response)
        else:
            output_list = inst_response

        return output_list

    @staticmethod
    def _squash_output_list(inst_for_user_list, full_inst_list):
        """Filter entries in the full instrument list."""
        inst_list = [i['id'] for i in inst_for_user_list]
        output_list = [obj for obj in full_inst_list if obj['id'] in inst_list]

        return output_list

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @tools.json_out()
    def GET(self, search_terms='', **kwargs):
        """CherryPy GET method."""
        user_id = kwargs['user'] if 'user' in kwargs else None
        return self._get_instruments_for_keywords(user_id, search_terms)
# pylint: enable=too-few-public-methods
