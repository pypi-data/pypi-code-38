import json
import logging

from orm_cloud.configuration import Configuration
from orm_cloud.database_adapters.database_factory import DatabaseFactory
from orm_cloud.database_adapters.ms_sql_adapter import MsSqlAdapter


class DatabaseAdapter:
    log = logging.getLogger(__name__)

    def __init__(self, config):
        self._config = config
        self._type = config.db_type

    def query(self, select, table, filter, sort_by=None, offset=None, limit=None, one_result=False):
        self.log.debug('Creating {} database adapter...'.format(self._type))
        if self._type == 'pymssql':
            adapter = MsSqlAdapter()
        else:
            # invalid database
            raise RuntimeError('The database type {} is not available.'.format(self._type))

        sql, where_replacements = adapter.get_sql(select, table, filter, sort_by, offset, limit)
        self.log.debug('SQL [replacement values] is {} [{}].'.format(sql, where_replacements))

        database_factory = DatabaseFactory(self._type, hostname=self._config.db_hostname, user=self._config.db_username,
                                           password=self._config.db_password, database=self._config.db_name)
        connection = database_factory.get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, where_replacements)
        r = [dict((cursor.description[i][0], value)
                  for i, value in enumerate(row)) for row in cursor.fetchall()]

        return (r[0] if r else None) if one_result else r












