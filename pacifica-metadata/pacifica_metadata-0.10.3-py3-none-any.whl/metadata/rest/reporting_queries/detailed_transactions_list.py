#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
from cherrypy import tools, request
from peewee import fn
from pacifica.metadata.rest.reporting_queries.query_base import QueryBase
from pacifica.metadata.orm import TransSIP, Files
from pacifica.metadata.orm.base import db_connection_decorator
from pacifica.metadata.rest.reporting_queries.summarize_by_date import SummarizeByDate


# pylint: disable=too-few-public-methods
class DetailedTransactionList(QueryBase):
    """Retrieves a list of all transactions matching the search criteria."""

    exposed = True

    @staticmethod
    def get_transaction_list_details(transaction_list):
        """Return complete data set on a specified transaction."""
        # pylint: disable=no-member
        query = (
            Files().select(
                Files.transaction.alias('upload_id'),
                fn.Max(TransSIP.updated).alias('upload_date'),
                fn.Min(Files.mtime).alias('file_date_start'),
                fn.Max(Files.mtime).alias('file_date_end'),
                fn.Min(TransSIP.submitter).alias('uploaded_by_id'),
                fn.Sum(Files.size).alias('bundle_size'),
                fn.Count(Files.id).alias('file_count'),
                fn.Min(TransSIP.updated).alias('upload_datetime'),
                fn.Min(TransSIP.project).alias('project_id'),
                fn.Min(TransSIP.instrument).alias('instrument_id')
            ).join(
                TransSIP,
                on=(TransSIP.id == Files.transaction)
            ).where(Files.transaction << transaction_list).group_by(Files.transaction)
        )
        # pylint: enable=no-member

        return {str(r['upload_id']): {
            'upload_id': str(r['upload_id']),
            'upload_date': r['upload_date'].date().strftime('%Y-%m-%d'),
            'file_date_start': SummarizeByDate.utc_to_local(r['file_date_start']).date().strftime('%Y-%m-%d'),
            'file_date_end': SummarizeByDate.utc_to_local(r['file_date_end']).date().strftime('%Y-%m-%d'),
            'uploaded_by_id': int(r['uploaded_by_id']),
            'bundle_size': int(r['bundle_size']),
            'file_count': int(r['file_count']),
            'upload_datetime': SummarizeByDate.utc_to_local(r['upload_date']).strftime('%Y-%m-%d %H:%M:%S'),
            'project_id': r['project_id'],
            'instrument_id': r['instrument_id']
        } for r in query.dicts()}

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_in()
    @tools.json_out()
    @db_connection_decorator
    def POST():
        """Return summaryinfo for a given object type/id/time range combo."""
        # parse object list
        transaction_list = request.json

        return DetailedTransactionList.get_transaction_list_details(transaction_list)
