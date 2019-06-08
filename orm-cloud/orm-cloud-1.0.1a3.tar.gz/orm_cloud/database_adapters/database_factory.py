import pymssql
import sqlite3


class DatabaseFactory:
    def __init__(self, type, **kwargs):
        self._type = type
        self._db_params = kwargs

        if type == 'sqllte':
            self._connection = sqlite3.connect(':memory:')
        if type == 'pymssql':
            self._connection = pymssql.connect(host=self._db_params['hostname'], user=self._db_params['user'],
                                               password=self._db_params['password'],
                                               database=self._db_params['database'])

    def get_connection(self):
        return self._connection

