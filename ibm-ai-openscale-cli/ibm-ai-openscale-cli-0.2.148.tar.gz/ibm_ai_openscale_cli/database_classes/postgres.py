# coding=utf-8
import psycopg2
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger

logger = FastpathLogger(__name__)

DROP_SCHEMA = u'DROP SCHEMA IF EXISTS {} CASCADE'
CREATE_SCHEMA = u'CREATE SCHEMA {}'
SELECT_TABLES_TO_DROP = u"SELECT table_name FROM information_schema.tables WHERE table_schema = '{}' and table_type = 'BASE TABLE'"
SELECT_METRICS_TABLES_TO_DROP = u"SELECT table_name FROM information_schema.tables WHERE table_schema = '{}' and table_type = 'BASE TABLE' and (table_name like 'Payload_%' or table_name like 'Feedback_%' or table_name like 'Manual_Labeling_%')"
DROP_TABLE = u'DROP TABLE "{}"."{}" CASCADE'
SELECT_TABLES_TO_DELETE_ROWS = u"SELECT table_name FROM information_schema.tables WHERE table_schema = '{}' and (table_name = 'MeasurementFacts' or table_name = 'Explanations' or table_name = 'Monitor_quality' or table_name like 'Payload_%' or table_name like 'Feedback_%' or table_name like 'Manual_Labeling_%')"
DELETE_TABLE_ROWS = u'DELETE FROM "{}"."{}"'

class Postgres(object):

    def __init__(self, user, password, hostname, port, dbname):
        conn_string = 'host=\'{}\' port=\'{}\' dbname=\'{}\' user=\'{}\' password=\'{}\''.format(hostname, port, dbname, user, password)
        self._connection = psycopg2.connect(conn_string)

    def _execute(self, statement_str, return_rows=False):
        with self._connection:  # transaction
            with self._connection.cursor() as cursor:
                cursor.execute(statement_str)
                if return_rows:
                    rows = cursor.fetchall()
                    return rows

    def drop_existing_schema(self, schema_name, keep_schema):
        if keep_schema:
            logger.log_debug('Dropping tables from schema {}'.format(schema_name))
            rows = self._execute(SELECT_TABLES_TO_DROP.format(schema_name), True)
            for row in rows:
                self._execute(DROP_TABLE.format(schema_name, row[0]))
            return
        logger.log_debug('Dropping schema {}'.format(schema_name))
        self._execute(DROP_SCHEMA.format(schema_name))

    def create_new_schema(self, schema_name, keep_schema):
        if keep_schema:
            return
        logger.log_debug('Creating schema {}'.format(schema_name))
        self._execute(CREATE_SCHEMA.format(schema_name))

    def reset_metrics_tables(self, schema_name):
        rows = self._execute(SELECT_TABLES_TO_DELETE_ROWS.format(schema_name), True)
        for row in rows:
            self._execute(DELETE_TABLE_ROWS.format(schema_name, row[0]))

    def drop_metrics_tables(self, schema_name):
        rows = self._execute(SELECT_METRICS_TABLES_TO_DROP.format(schema_name), True)
        for row in rows:
            self._execute(DROP_TABLE.format(schema_name, row[0]))
