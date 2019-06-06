from mlcore.datahelper.athena.athena_helper import AthenaHelper
from mlcore.datahelper.athena.mllearningdb.create import Creator
from mlcore.datahelper.athena.mllearningdb.update import Updater

from datetime import datetime
import json

import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')


class DataHelper(AthenaHelper):

    def __init__(self, config):

        self.config = config['mlcore']['datahelper']['athena']['mllearningdb']
        super().__init__(self.config)
        self.logger = logging.getLogger(self.__class__.__name__)

    def connect(self):
        super().connect()


    def create_table(self, table, database):
        sql = {
            'battery_swap_log': Creator().create_battery_swap_log(database),
            'vm_status': Creator().create_vm_status(database)
        }[table]
        self.query(sql, database)

    def add_partition(self, table, database, pkey, pvalue, s3path):
        sql = Updater().add_partition(table, database, pkey, pvalue, s3path)
        self.query(sql, database)

        sql = Updater().set_partition_location(table, database, pkey, pvalue, s3path)
        self.query(sql, database)

    
