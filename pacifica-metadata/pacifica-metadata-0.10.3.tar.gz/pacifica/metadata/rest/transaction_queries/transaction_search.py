#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
import cherrypy
# import re
from cherrypy import tools, HTTPError
from peewee import Expression, OP
from pacifica.metadata.rest.transaction_queries.query_base import QueryBase
from pacifica.metadata.orm import TransSIP
from pacifica.metadata.orm.base import db_connection_decorator


class TransactionSearch(QueryBase):
    """Retrieves a list of all transactions matching the search criteria."""

    exposed = True

    @staticmethod
    def _search_transactions(search_terms):
        # build the search query from keyword bits
        trans = TransSIP()
        where_clause = Expression(1, OP.EQ, 1)
        query = trans.select()
        item_count = 100
        page_num = -1
        offset = -1
        for term in search_terms:
            value = str(search_terms[term]).replace('+', ' ')
            if term in ['project', 'project_id'] and value != '-1':
                where_clause &= TransSIP().where_clause(
                    {'project': value})
                continue
            if term in ['instrument', 'instrument_id'] and value != '-1':
                where_clause &= TransSIP().where_clause(
                    {'instrument': value})
                continue
            if term in ['start', 'start_time']:
                where_clause &= TransSIP().where_clause(
                    {'updated': value, 'updated_operator': 'gte'})
                continue
            if term in ['end', 'end_time']:
                where_clause &= TransSIP().where_clause(
                    {'updated': value, 'updated_operator': 'lte'})
                continue
            if term in ['user', 'user_id', 'person',
                        'person_id', 'submitter', 'submitter_id'] and value != '-1':
                where_clause &= TransSIP().where_clause(
                    {'submitter': value})
                continue
            if term in ['transaction_id'] and value != '-1':
                where_clause &= TransSIP().where_clause({'_id': value})
                continue
            if term in ['item_count'] and value != '-1':
                item_count = int(value)
            if term in ['page'] and value != '-1':
                page_num = int(value)
        query = query.where(where_clause)
        total_transaction_count = query.count()
        if item_count > 0 and (page_num > 0 or offset >= 0):
            offset = item_count * (page_num - 1)
            query = query.limit(item_count).offset(offset)

        query = query.order_by(TransSIP.id.desc())

        transaction_search_stats = {
            'total_count': total_transaction_count,
            'items_per_page': item_count,
            'page': page_num,
            'offset': offset
        }

        return [t.id for t in query], transaction_search_stats

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(option='details', **kwargs):
        """Return transactions for the search params."""
        option = 'details' if option not in ['list', 'details'] else option

        kwargs = {k: v for (k, v) in kwargs.items()
                  if k in QueryBase.valid_keywords}
        if not kwargs:
            message = 'Invalid transaction details search request. '
            cherrypy.log.error(message)
            raise HTTPError(
                '400 Invalid Request Options',
                QueryBase.compose_help_block_message()
            )
        else:
            transactions, transaction_search_stats = TransactionSearch._search_transactions(
                kwargs)

        results = QueryBase._get_transaction_info_blocks(transactions, option)
        results.update(transaction_search_stats)
        return results
