from mlcore.datahelper.mongodb.mongodb_data_helper import MongoDBDataHelper
from mlcore.datahelper.mongodb.dataplatform import find as Finder
import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

class DataHelper(MongoDBDataHelper):

    def __init__(self, config):

        self.config = config['mlcore']['datahelper']['mongodb']['dataplatform']
        super().__init__(self.config)
        self.logger = logging.getLogger(self.__class__.__name__)

    def connect(self):
        super().connect()

    #def get_battery_swap_log_b(self, start_ts, end_ts=0):
    #    return super().find(
    #        Finder.CollectionNames().battery_swap_log_b, 
    #        Finder.get_battery_swap_log(start_ts, end_ts))

    def get_battery_swap_log(self, start_ts, end_ts=0):
        return super().find(
            Finder.CollectionNames().battery_swap_log, 
            Finder.get_battery_swap_log(start_ts, end_ts))

    #def get_vm_status_b(self, start_ts, end_ts=0):
    #    return super().find(
    #        Finder.CollectionNames().vm_status_b, 
    #        Finder.get_vm_status(start_ts, end_ts))

    def get_vm_status(self, start_ts, end_ts=0):
        return super().find(
            Finder.CollectionNames().vm_status, 
            Finder.get_vm_status(start_ts, end_ts))
