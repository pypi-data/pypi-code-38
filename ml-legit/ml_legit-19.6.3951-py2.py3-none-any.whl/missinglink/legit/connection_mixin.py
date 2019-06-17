# -*- coding: utf-8 -*-


class ConnectionMixin(object):
    def __init__(self, connection):
        self.__connection = connection

        super(ConnectionMixin, self).__init__()

    @property
    def _connection(self):
        return self.__connection

    def close(self):
        self._connection.close()
