#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
import datetime
from calendar import monthrange
from cherrypy import tools
from dateutil.parser import parse
from peewee import Expression, OP
from pacifica.metadata.rest.transaction_queries.query_base import QueryBase
from pacifica.metadata.orm import TransSIP, InstrumentGroup
from pacifica.metadata.orm.base import db_connection_decorator
from pacifica.metadata.rest.reporting_queries.detailed_transactions_list import DetailedTransactionList


class TransactionsMultiSearch(QueryBase):
    """Retrieves a list of all transactions matching the search criteria."""

    exposed = True

    @staticmethod
    def _get_transactions_from_group(instrument_group_id, project_id, start_time, end_time):
        instrument_list = TransactionsMultiSearch._get_instruments_from_group_id(
            instrument_group_id)

        where_clause = Expression(1, OP.EQ, 1)
        # now get the approjriate transactions
        where_clause &= TransSIP().where_clause(
            {'updated': start_time, 'updated_operator': 'gte'})
        where_clause &= TransSIP().where_clause(
            {'updated': end_time, 'updated_operator': 'lte'})

        if instrument_list:
            where_clause &= (TransSIP.instrument << instrument_list)
        if project_id:
            where_clause &= (TransSIP.project == project_id)
        transactions_list_query = TransSIP.select(
            TransSIP.id).where(where_clause)

        transactions_list = [t['id'] for t in transactions_list_query.dicts()]
        return transactions_list

    @staticmethod
    def _get_instruments_from_group_id(group_id):
        instrument_list_query = (InstrumentGroup
                                 .select(InstrumentGroup.instrument)
                                 .where(InstrumentGroup.group == group_id).dicts())
        instrument_list = [i['instrument'] for i in instrument_list_query]
        return instrument_list

    @staticmethod
    def _get_first_last_day():
        today = datetime.datetime.today()
        last_day = monthrange(today.year, today.month)[1]
        return (today.replace(day=1).date(), today.replace(day=last_day).date())

    @staticmethod
    def _check_keywords(kwargs):
        valid_keywords = ['project_id',
                          'instrument_group_id', 'start_time', 'end_time']
        return {k: v for (k, v) in kwargs.items() if k in valid_keywords}

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(**kwargs):
        """Return Transactions for a project_id and instrument_group_id."""
        first_day_of_month, last_day_of_month = TransactionsMultiSearch._get_first_last_day()
        kwargs = TransactionsMultiSearch._check_keywords(kwargs)

        instrument_group_id = kwargs['instrument_group_id'] if 'instrument_group_id' in kwargs else None
        project_id = kwargs['project_id'] if 'project_id' in kwargs else None
        start_time = parse(
            kwargs['start_time']) if 'start_time' in kwargs else first_day_of_month
        end_time = parse(
            kwargs['end_time']) if 'end_time' in kwargs else last_day_of_month

        transaction_list = TransactionsMultiSearch._get_transactions_from_group(
            instrument_group_id, project_id,
            start_time.strftime('%Y-%m-%d'),
            end_time.strftime('%Y-%m-%d'))

        return DetailedTransactionList.get_transaction_list_details(transaction_list)
