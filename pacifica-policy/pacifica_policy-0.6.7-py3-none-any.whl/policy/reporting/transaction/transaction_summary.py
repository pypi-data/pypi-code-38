#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
from six import text_type
import requests
from cherrypy import tools, request
from pacifica.policy.validation import validate_user
from pacifica.policy.config import get_config
from pacifica.policy.reporting.transaction.query_base import QueryBase


# pylint: disable=too-few-public-methods
class TransactionSummary(QueryBase):
    """Retrieves a summary of all transactions matching the search criteria."""

    exposed = True

    @staticmethod
    # pylint: disable=too-many-arguments
    def _get_transaction_list_summary(
            time_basis, object_list, object_type, start_date, end_date, user_id
    ):
        header_list = {'Content-Type': 'application/json'}
        url = '{0}/summaryinfo/by_date/'.format(
            get_config().get('metadata', 'endpoint_url')
        )
        url += '{0}/{1}/{2}/{3}'.format(
            time_basis, object_type, start_date, end_date
        )
        req = requests.post(
            url=url,
            json=object_list,
            headers=header_list
        )
        user_info = QueryBase._merge_two_dicts(
            QueryBase.base_user_info,
            QueryBase.get_full_user_info(user_id),
        )

        req_json = req.json()

        types_to_check = ['instrument', 'project']

        for entry_type in types_to_check:
            req_json['summary_totals']['upload_stats'][entry_type] = TransactionSummary._cleanup_object_stats(
                object_listing=req_json['summary_totals']['upload_stats'][entry_type],
                object_type=entry_type,
                user_info=user_info
            )

        return req_json

    @staticmethod
    def _cleanup_object_stats(object_listing, object_type, user_info):
        valid_object_list = map(text_type, user_info[object_type + '_list'])
        clean_object_stats = {}
        for object_id, object_stats in object_listing.items():
            if object_id in valid_object_list or user_info['emsl_employee']:
                clean_object_stats[object_id] = object_stats
            else:
                if 'Other' not in clean_object_stats.keys():
                    clean_object_stats['Other'] = 0
                clean_object_stats['Other'] += object_stats
        return clean_object_stats

    # pylint: enable=too-many-arguments

    # CherryPy requires these named methods
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_in()
    @tools.json_out()
    @validate_user('user')
    def POST(time_basis=None, object_type=None, start_date=None, end_date=None, **kwargs):
        """CherryPy GET method."""
        object_list = request.json
        user_id = kwargs['user']
        return TransactionSummary._get_transaction_list_summary(
            time_basis, object_list, object_type, start_date, end_date, user_id
        )
# pylint: enable=too-few-public-methods
