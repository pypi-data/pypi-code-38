# -*- coding: utf-8 -*-
import copy
import logging
from abc import ABCMeta, abstractmethod

import datetime
import six
import sys

from ..connection_mixin import ConnectionMixin


class MetadataOperationError(Exception):
    pass


class MetadataTypeNotSupported(MetadataOperationError):
    pass


class MetadataFieldNotFound(MetadataOperationError):
    def __init__(self, field=None):  # pickle storage
        self._field = field

    @property
    def field(self):
        return self._field

    def __str__(self):
        return 'Metadata field %s not found' % self.field


def unicode_dict_to_str(d):
    if sys.version_info >= (3, 0):
        return d

    for key, val in d.items():
        if not isinstance(val, unicode):
            continue

        d[key] = val.encode('utf8')

    return d


class BaseMetadataDB(ConnectionMixin):
    __metaclass__ = ABCMeta

    STAGING_COMMIT = 'staging'
    DEFAULT_SEED = 1337
    DEFAULT_SPLIT = {'train': 0.6, 'test': 0.2, 'validation': 0.2}

    def __init__(self, connection, version_ts_lookup=None, **kwargs):
        super(BaseMetadataDB, self).__init__(connection)
        self.__rnd = None
        self.__prev_table_info = None
        self.__create_table_if_needed()
        self.__version_ts_lookup = version_ts_lookup

    @abstractmethod
    def _create_table(self):
        """

        :return:
        """

    @abstractmethod
    def _add_missing_columns(self, data_object):
        """

        :param data_object:
        :return:
        """

    @abstractmethod
    def _add_data(self, flatten_data_list):
        """

        :param flatten_data_list:
        :return:
        """

    @abstractmethod
    def get_data_for_commit(self, sha, commit_sha):
        """

        :param sha:
        :param commit_sha:
        :return:
        """

    @abstractmethod
    def get_all_data(self, sha):
        """

        :param sha:
        :return:
        """

    @abstractmethod
    def begin_commit(self, commit_sha, tree_id, ts):
        """

        :param commit_sha:
        :param tree_id:
        :return:
        """

    @abstractmethod
    def end_commit(self):
        """

        :param commit_sha:
        :param tree_id:
        :return:
        """

    @abstractmethod
    def _query(self, sql_vars, select_fields, where, **kwargs):
        """

        :param sql_vars:
        :param select_fields:
        :param where:
        :return:
        """

    def __create_table_if_needed(self):
        if self._connection.read_only:
            return

        self._create_table()

    def add_data(self, data):
        if not data:
            logging.debug('no data provided')
            return

        if not isinstance(data, list):
            data = [data]

        logging.debug('add data (total: %s)', len(data))

        data_list = []
        for sha, data_object in data:
            data_object_clone = copy.deepcopy(data_object)

            self._add_missing_columns(data_object)

            data_object_clone['@sha'] = sha
            data_object_clone['@commit_sha'] = self.STAGING_COMMIT
            data_object_clone['@version'] = 2 ** 32 - 1
            data_object_clone['@hash'] = None

            data_list.append(data_object_clone)

        self._add_data(data_list)

    def explicit_query(self, query_text):
        from ..scam import QueryParser, tree_to_sql_parts

        tree = QueryParser().parse_query(query_text)
        sql_vars, _ = tree_to_sql_parts(tree, self._connection.create_sql_helper())

        sql_vars = sql_vars or {}

        if 'seed' not in sql_vars:
            query_text += ' @seed:%s' % self.DEFAULT_SEED

        return query_text

    def query(self, query_text, **kwargs):
        from ..scam import QueryParser, tree_to_sql_builder, get_split_vars, ParseError

        from pyparsing import ParseException

        if query_text is not None and not isinstance(query_text, str):
            query_text = query_text.encode('utf8')

        try:
            tree = QueryParser().parse_query(query_text)
            sql_builder = tree_to_sql_builder(tree, self._connection.create_sql_helper())

            sql_vars = sql_builder.build_vars()
            where = sql_builder.build_where()
            has_complex_data = sql_builder.has_complex_data
        except ParseException:
            raise ParseError()

        select_fields = ['*']

        sql_vars = sql_vars or {}

        if 'seed' not in sql_vars:
            sql_vars['seed'] = self.DEFAULT_SEED

        if 'phase_train_start' not in sql_vars:
            sql_vars.update(get_split_vars(self.DEFAULT_SPLIT))

        sql_vars['version_ts'] = datetime.datetime.utcnow()
        if 'version' in sql_vars:
            version = sql_vars['version']
            if self.__version_ts_lookup is not None:
                sql_vars['version_ts'] = self.__version_ts_lookup(version)

        if 'sample_percentile' not in sql_vars:
            sql_vars['sample_percentile'] = 0.0
            sql_vars['sample'] = 1.0

        return self._query(sql_vars, select_fields, where, has_complex_data=has_complex_data, **kwargs)

    @classmethod
    def fill_in_vars(cls, query_sql, sql_vars):
        var_keys = sorted(sql_vars.keys(), reverse=True)
        for var_name in var_keys:
            var_value = sql_vars[var_name]
            query_sql = query_sql.replace('$' + var_name, str(var_value))

        return query_sql

    def _return_all_result_from_query(self, query_sql, batch_size=1000):
        from flatten_json import unflatten

        with self._connection.get_cursor() as c:
            c.execute(query_sql)

            while True:
                results = c.fetchmany(batch_size)
                if not results:
                    break

                for result in results:
                    yield unflatten(unicode_dict_to_str(result), separator='.')
