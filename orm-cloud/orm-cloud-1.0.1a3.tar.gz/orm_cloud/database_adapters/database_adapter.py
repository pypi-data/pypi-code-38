import json
import logging

from orm_cloud.configuration import Configuration
from orm_cloud.database_adapters.database_factory import DatabaseFactory
from orm_cloud.database_adapters.ms_sql_adapter import MsSqlAdapter


class DatabaseAdapter:
    log = logging.getLogger(__name__)

    def __init__(self, type, **kwargs):
        self._type = type
        self._db_params = kwargs

    def query(self, select, table, filter, sort_by=None, offset=None, limit=None, one_result=False):
        config = Configuration()
        db_info = config.db_info
        db_info_json = json.loads(db_info)

        self.log.debug('Creating {} database adapter...'.format(self._type))
        if self._type == 'pymssql':
            adapter = MsSqlAdapter()
        else:
            # invalid database
            raise RuntimeError('The database type {} is not available.'.format(self._type))

        sql = adapter.get_sql(select, table, filter, sort_by, offset, limit)
        self.log.debug('SQL is [{}].'.format(sql))

        database_factory = DatabaseFactory(self._type, hostname=db_info_json['host'], user=db_info_json['username'],
                                           password=db_info_json['password'], database=db_info_json['dbInstanceIdentifier'])
        connection = database_factory.get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, None)
        r = [dict((cursor.description[i][0], value)
                  for i, value in enumerate(row)) for row in cursor.fetchall()]

        return (r[0] if r else None) if one_result else r












