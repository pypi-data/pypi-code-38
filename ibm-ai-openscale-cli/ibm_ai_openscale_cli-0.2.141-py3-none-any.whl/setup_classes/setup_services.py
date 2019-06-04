# coding=utf-8
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict
import json
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger

logger = FastpathLogger(__name__)

class SetupServices(object):

    def __init__(self, args):
        self._args = args

    def read_credentials_from_file(self, credentials_file):
        logger.log_info('Using credentials from "{}"'.format(credentials_file))
        return jsonFileToDict(credentials_file)

    def setup_postgres_database(self):
        credentials = None
        if self._args.postgres or self._args.postgres_json:
            logger.log_info('Compose for PostgreSQL instance specified')
            if self._args.postgres_json:
                credentials = json.loads(self._args.postgres_json)
            else:
                credentials = self.read_credentials_from_file(self._args.postgres)
        return credentials

    def setup_icd_database(self):
        credentials = None
        if self._args.icd or self._args.icd_json:
            logger.log_info('ICD instance specified')
            if self._args.icd_json:
                credentials = json.loads(self._args.icd_json)
            else:
                credentials = self.read_credentials_from_file(self._args.icd)
            credentials['db_type'] = 'postgresql'
            connection_data = credentials['connection']['postgres']
            hostname = connection_data['hosts'][0]['hostname']
            port = connection_data['hosts'][0]['port']
            dbname = connection_data['database']
            user = connection_data['authentication']['username']
            password = connection_data['authentication']['password']
            credentials['uri'] = 'postgres://{}:{}@{}:{}/{}'.format(user, password, hostname, port, dbname)
        return credentials

    def setup_db2_database(self):
        credentials = None
        if self._args.db2 or self._args.db2_json:
            logger.log_info('DB2 instance specified')
            if self._args.db2_json:
                credentials = json.loads(self._args.db2_json)
            else:
                credentials = self.read_credentials_from_file(self._args.db2)
            credentials['db_type'] = 'db2'
        return credentials
