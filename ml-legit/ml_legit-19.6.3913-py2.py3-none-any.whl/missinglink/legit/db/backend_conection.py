# -*- coding: utf-8 -*-
from .base_connection import BaseConnection


class BackendConnection(BaseConnection):
    def __init__(self, data_volume_config, session, **kwargs):
        self.__session = session
        super(BackendConnection, self).__init__(data_volume_config, **kwargs)

    def _create_connection(self, **kwargs):
        return self.__session

    def _create_cursor(self):
        return self.__session

    def _rollback(self):
        raise NotImplementedError(self._rollback)

    def create_sql_helper(self):
        raise NotImplementedError(self.create_sql_helper)

    def _commit(self):
        raise NotImplementedError(self._commit)
