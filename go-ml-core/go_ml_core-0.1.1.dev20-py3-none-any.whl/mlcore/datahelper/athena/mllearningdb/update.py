import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

class Updater():
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_partition(self, table, database, pkey, pvalue, s3path):
        sql = '''
ALTER TABLE %s.%s 
ADD PARTITION (`%s`='%s') 
LOCATION '%s';
        ''' % (database, table, pkey, pvalue, s3path)

        return sql

    def set_partition_location(self, table, database, pkey, pvalue, s3path):
        sql = '''
ALTER TABLE %s.%s  
PARTITION (`%s`='%s')
SET LOCATION '%s';
        ''' % (database, table, pkey, pvalue, s3path)
        return sql