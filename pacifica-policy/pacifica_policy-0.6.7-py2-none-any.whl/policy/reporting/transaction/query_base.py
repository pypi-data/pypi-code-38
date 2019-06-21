#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata projectinfo base class."""
import requests
from pacifica.policy.config import get_config


# pylint: disable=too-few-public-methods
class QueryBase(object):
    """Formats summary data for other classes down the tree."""

    base_user_info = {
        'emsl_employee': False,
        'project_list': [],
        'instrument_list': []
    }

    @staticmethod
    def _get_user_lookups(url, header_list):
        req = requests.get(
            url=url, headers=header_list
        )
        infolist = [i['id'] for i in req.json() if i]
        return infolist

    @staticmethod
    def get_full_user_info(user_id):
        """Return user information for the given user_id."""
        header_list = {'Content-Type': 'application/json'}
        user_info_request = requests.get(
            url='{0}/userinfo/by_id/{1}'.format(
                get_config().get('metadata', 'endpoint_url'), user_id),
            headers=header_list
        )
        if user_info_request.status_code != 200:
            return None

        user_info = user_info_request.json()

        # get available projects for this user
        proj_list = QueryBase._get_user_lookups(
            '{0}/projectinfo/by_user_id/{1}'.format(
                get_config().get('metadata', 'endpoint_url'),
                user_id
            ),
            header_list
        )
        # get available instruments for this user
        inst_list = QueryBase._get_user_lookups(
            url='{0}/instrumentinfo/by_user_id/{1}'.format(
                get_config().get('metadata', 'endpoint_url'),
                user_id
            ),
            header_list=header_list
        )
        user_info['project_list'] = proj_list
        user_info['instrument_list'] = inst_list

        return user_info

    @staticmethod
    def _merge_two_dicts(dict_a, dict_b):
        """Given two dicts, merge them into a new dict as a shallow copy."""
        dict_out = dict_a.copy()
        if dict_b:
            dict_out.update(dict_b)
        return dict_out
