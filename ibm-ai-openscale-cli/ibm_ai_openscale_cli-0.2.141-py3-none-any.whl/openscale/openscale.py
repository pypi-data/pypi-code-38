# coding=utf-8

from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
import time
from ibm_ai_openscale import APIClient, APIClient4ICP

logger = FastpathLogger(__name__)

class OpenScale:

    DEFAULT_DATAMART_SCHEMA_NAME = 'wosfastpath'

    def __init__(self, args, credentials, database_credentials):
        self._args = args
        self._credentials = credentials
        self._keep_schema = self._args.keep_schema
        self._verify = False if self._args.is_icp else True
        self._database_credentials = database_credentials
        self._database = self._get_database()
        start = time.time()
        self._client = APIClient4ICP(credentials) if self._args.is_icp else APIClient(credentials)
        elapsed = time.time() - start
        self._datamart_name = self._get_datamart_name()
        logger.log_info('Using {} Python Client version: {}'.format(self._args.service_name, self._client.version))
        logger.log_debug('TIMER: Connect to APIClient in {:.3f} seconds'.format(elapsed))

    def _get_datamart_name(self):
        datamart_name = self._args.datamart_name
        if datamart_name is None:
            if self._database_credentials: # use the datamart database connection user id
                if self._database_credentials['db_type'] == 'postgresql':
                    if 'connection' in self._database_credentials and 'postgres' in self._database_credentials['connection']: # icd
                        datamart_name = self._database_credentials['connection']['postgres']['authentication']['username']
                    else: # compose
                        datamart_name = self._database_credentials['uri'].split('@')[0].split('//')[1].split(':')[0]
                elif self._database_credentials['db_type'] == 'db2':
                    datamart_name = self._database_credentials['username']
                else:
                    raise Exception('Invalid database type specified. Only "postgresql" and "db2" are supported.')
            else:
                datamart_name = OpenScale.DEFAULT_DATAMART_SCHEMA_NAME # for internal database
        self._args.datamart_name = datamart_name
        return datamart_name

    def _get_database(self):
        if not self._database_credentials:
            return None
        if self._database_credentials['db_type'] == 'postgresql':
            if 'connection' in self._database_credentials and 'postgres' in self._database_credentials['connection']: # icd
                from ibm_ai_openscale_cli.database_classes.postgres_icd import PostgresICD
                return PostgresICD(self._database_credentials)
            else: # compose
                from ibm_ai_openscale_cli.database_classes.postgres_compose import PostgresCompose
                return PostgresCompose(self._database_credentials)
        elif self._database_credentials['db_type'] == 'db2':
            from ibm_ai_openscale_cli.database_classes.db2 import DB2, validate_db2_credentials
            self._database_credentials = validate_db2_credentials(self._database_credentials)
            return DB2(self._database_credentials)
        else:
            raise Exception('Invalid database type specified. Only "postgresql" and "db2" are supported.')
