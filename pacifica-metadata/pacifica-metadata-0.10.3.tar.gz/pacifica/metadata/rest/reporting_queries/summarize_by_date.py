#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
import datetime
import pytz
from dateutil.parser import parse
from cherrypy import tools, request
from peewee import Expression, OP
from pacifica.metadata.rest.reporting_queries.query_base import QueryBase
from pacifica.metadata.orm import TransSIP, Files
from pacifica.metadata.orm.base import db_connection_decorator


# pylint: disable=too-few-public-methods
class SummarizeByDate(QueryBase):
    """Retrieves a list of all transactions matching the search criteria."""

    exposed = True

    # pylint: disable=too-many-locals
    @staticmethod
    def _search_by_dates(object_type, object_id_list, start_date, end_date, time_basis):
        time_column_name = QueryBase.time_basis_mappings.get(time_basis)
        object_type_column_name = QueryBase.object_type_mappings.get(
            object_type)

        if time_basis == 'submitted':
            time_column = getattr(TransSIP, time_column_name)
        else:
            time_column = getattr(Files, time_column_name)
        object_type_column = getattr(TransSIP, object_type_column_name)

        where_clause = Expression(time_column, OP.GTE, start_date)
        where_clause &= Expression(time_column, OP.LTE, end_date)
        where_clause &= (object_type_column << object_id_list)
        query = Files().select(
            Files.id, time_column.alias(
                'filedate'), Files.size, Files.transaction
        ).join(TransSIP, on=(TransSIP.id == Files.transaction))

        # pylint: disable=no-member
        query = query.where(where_clause).order_by(time_column).objects()
        # pylint: enable=no-member

        results = {
            'day_graph': {
                'by_date': {
                    'available_dates': {},
                    'file_count': {},
                    'file_volume': {},
                    'transactions': {},
                    'file_volume_array': {},
                    'transaction_count_array': {}
                }
            },
            'summary_totals': {
                'upload_stats': {
                    'project': {},
                    'instrument': {},
                    'user': {}
                },
                'total_file_count': 0,
                'total_size_bytes': 0,
                'total_size_string': ''
            },
            'transaction_info': {
                'transaction': {},
                'project': {},
                'instrument': {},
                'user': {}
            }
        }

        transaction_cache = {}
        for item in query.iterator():
            if item.transaction_id not in transaction_cache:
                t_info = item.transaction.transsip.get().to_hash()
                transaction_cache[item.transaction_id] = t_info
            else:
                t_info = transaction_cache[item.transaction_id]
            SummarizeByDate._summarize_by_date(
                results['day_graph']['by_date'], item)

            SummarizeByDate._update_transaction_info_block(
                results['transaction_info'], item, t_info)

            SummarizeByDate._summarize_upload_stats(
                results['summary_totals']['upload_stats'], t_info)

            results['summary_totals']['total_file_count'] += 1
            results['summary_totals']['total_size_bytes'] += item.size
        return results
    # pylint: enable=too-many-locals

    @staticmethod
    def _update_transaction_info_block(info_block, item, t_info):
        proj = t_info['project']
        inst = t_info['instrument']
        submitter = t_info['submitter']
        transsip = item.transaction.transsip.get()
        if proj not in info_block['project'].keys():
            info_block['project'][proj] = transsip.project.title
        if inst not in info_block['instrument'].keys():
            info_block['instrument'][inst] = transsip.instrument.name
        if submitter not in info_block['user'].keys():
            info_block['user'][submitter] = u'{0} {1}'.format(
                transsip.submitter.first_name, transsip.submitter.last_name
            )

    @staticmethod
    def _summarize_upload_stats(upload_stats_block, transaction_info):
        if transaction_info['project'] not in upload_stats_block['project'].keys():
            upload_stats_block['project'][transaction_info['project']] = 0
        upload_stats_block['project'][transaction_info['project']] += 1

        if transaction_info['instrument'] not in upload_stats_block['instrument'].keys():
            upload_stats_block['instrument'][transaction_info['instrument']] = 0
        upload_stats_block['instrument'][transaction_info['instrument']] += 1

        if transaction_info['submitter'] not in upload_stats_block['user'].keys():
            upload_stats_block['user'][transaction_info['submitter']] = 0
        upload_stats_block['user'][transaction_info['submitter']] += 1

    @staticmethod
    def _summarize_by_date(summary_block, item):
        current_day = SummarizeByDate.utc_to_local(item.filedate).date()
        current_day = current_day.strftime('%Y-%m-%d')
        if current_day not in summary_block['file_count'].keys():
            summary_block['file_count'][current_day] = 0
        if current_day not in summary_block['file_volume'].keys():
            summary_block['file_volume'][current_day] = 0
        if current_day not in summary_block['transactions'].keys():
            summary_block['transactions'][current_day] = []
        summary_block['file_count'][current_day] += 1
        summary_block['file_volume'][current_day] += item.size
        if item.transaction_id not in summary_block['transactions'][current_day]:
            summary_block['transactions'][current_day].append(
                item.transaction.id)

        # return summary_block

    @staticmethod
    def local_to_utc(local_datetime_obj):
        """Return a TZ corrected datetime object."""
        utc_datetime_obj = QueryBase.local_timezone.localize(
            local_datetime_obj)
        return utc_datetime_obj.astimezone(pytz.utc)

    @staticmethod
    def utc_to_local(utc_datetime_obj):
        """Return a TZ corrected datetime object."""
        local_datetime_obj = pytz.utc.localize(utc_datetime_obj)
        return local_datetime_obj.astimezone(QueryBase.local_timezone)

    @staticmethod
    def _canonicalize_dates(start_date, end_date):
        try:
            start_date_obj = SummarizeByDate.local_to_utc(parse(start_date))
        except ValueError:
            start_date_obj = SummarizeByDate.local_to_utc(parse('1997-01-01'))
        try:
            end_date_obj = SummarizeByDate.local_to_utc(parse(end_date))
        except ValueError:
            end_date_obj = SummarizeByDate.local_to_utc(
                datetime.datetime.now())

        return start_date_obj.isoformat(), end_date_obj.isoformat()

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_in()
    @tools.json_out()
    @db_connection_decorator
    def POST(time_basis=None, object_type=None, start_date=None, end_date=None):
        """Return summaryinfo for a given object type/id/time range combo."""
        # check time basis validity
        time_basis_list = {'creat': 'created',
                           'modif': 'modified', 'submi': 'submitted'}
        if time_basis[0:5] not in time_basis_list.keys() or time_basis is None:
            time_basis = 'modified'
        else:
            time_basis = time_basis_list[time_basis[0:5]]

        object_type_list = ['instrument', 'project', 'user']
        if object_type not in object_type_list or object_type is None:
            object_type = 'instrument'

        # check start/end date validity
        start_date, end_date = SummarizeByDate._canonicalize_dates(
            start_date, end_date)

        return SummarizeByDate._search_by_dates(
            object_type, request.json,
            start_date, end_date, time_basis)
