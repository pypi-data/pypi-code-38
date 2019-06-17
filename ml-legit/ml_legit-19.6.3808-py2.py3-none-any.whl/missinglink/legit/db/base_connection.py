# -*- coding: utf-8 -*-
import logging
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager


class BaseConnection(object):
    __metaclass__ = ABCMeta

    def __init__(self, data_volume_config, **kwargs):
        self.read_only = kwargs.get('read_only', False)
        self.data_volume_config = data_volume_config
        self.__conn = self._create_connection(**kwargs)
        self.__in_transactions = False
        self.__cursor = None

    @contextmanager
    def get_cursor(self):
        should_close = self.__cursor is None
        return_cursor = None
        try:
            return_cursor = self._create_cursor() if self.__cursor is None else self.__cursor
            yield return_cursor
        finally:
            if should_close and return_cursor is not None and hasattr(return_cursor, 'close'):
                return_cursor.close()

    def commit(self):
        if self.__in_transactions:
            logging.info('db in transaction commit will be skipped')
            return

        self._commit()

    def close(self):
        if self.__conn is not None and hasattr(self.__conn, 'close'):
            self.__conn.close()

    @property
    def _native_conn(self):
        return self.__conn

    @abstractmethod
    def _create_cursor(self):
        """

        :return:
        """

    @abstractmethod
    def _commit(self):
        """

        :return:
        """

    @abstractmethod
    def _rollback(self):
        """

        :return:
        """

    @abstractmethod
    def create_sql_helper(self):
        """

        :return:
        """

    @abstractmethod
    def _create_connection(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

    def start_transactions(self):
        self.__in_transactions = True
        self.__cursor = self._create_cursor()

    def end_transactions(self):
        self._commit()
        self.__in_transactions = False

        if hasattr(self.__cursor, 'close'):
            self.__cursor.close()

    def rollback_transactions(self):
        self._rollback()
        self.__in_transactions = False
        if hasattr(self.__cursor, 'close'):
            self.__cursor.close()
