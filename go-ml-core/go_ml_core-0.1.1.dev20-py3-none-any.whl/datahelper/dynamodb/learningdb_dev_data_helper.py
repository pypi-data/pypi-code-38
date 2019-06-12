from datahelper.dynamodb.dynamodb_data_helper import DynamoDBDataHelper
from datahelper.dynamodb.ml_learning_dev import create as Creator
from datahelper.dynamodb.ml_learning_dev import update as Updator
from datetime import datetime
import json

from boto3.dynamodb.conditions import Key

class DataHelper(DynamoDBDataHelper):

    def __init__(
        self, 
        logger=None,
        config_file='go_servers.ini',
        host_name='ML_Learning_DEV'):
        super().__init__( 
            logger=logger,
            config_file=config_file,
            host_name=host_name)

    def connect(self):
        super().connect()
    
    def create_vm(self):
        table = self.create_table(Creator.vm)

        return table

    def create_battey_swap_log(self):
        table = self.create_table(Creator.battey_swap_log)

        return table

    def create_vm_status(self):
        table = self.create_table(Creator.vm_status)

        return table

    def update_battey_swap_log(self):
        table = self.update_table(Updator.battey_swap_log)

        return table

    def delete_vm(self):
        table = self.delete_table(Creator.vm['TableName'])

        return table

    def delete_battey_swap_log(self):
        table = self.delete_table(Creator.battey_swap_log['TableName'])

        return table

    def delete_vm_status(self):
        table = self.delete_table(Creator.vm_status)

        return table

    def query_battery_swap_log_by_date(self, dt_str):
        table = self.get_table(Creator.battey_swap_log['TableName'])
        filtering_exp = Key('ExchangeDate').eq(dt_str)
        response = table.query(KeyConditionExpression=filtering_exp)
        result = response['Items']
        if self.logger != None:
            self.logger.info('result.count = %s' % len(result))
            if len(result) > 0:
                self.logger.info('result[0] = %s' % result[0])

    def insert_vm(self, item_dict_list):
        item_list = []
        for item_dict in item_dict_list:
            dt = int(datetime.utcnow().timestamp())
            item = {
                'Id': item_dict['vm_guid'], 
                'Info': json.dumps(item_dict),
                'UpdateTime': dt}
            item_list.append(item)
            
        self.iterate_put_items(
            Creator.vm['TableName'],
            item_list)

    def insert_battey_swap_log(self, item_dict_list):
        if (len(item_dict_list))==0:
            self.logger.warn('Empty input of battey swap log')
            return

        item_list = []
        for item_dict in item_dict_list:
            [date_str, time_str] = self.timestamp_to_dt_str(item_dict['exchange_time'])
            item = {
                'ExchangeDate': date_str,
                'ExchangeTime#Id': '%s#%s' % (time_str, item_dict['_id']),
                'SwapLog': json.dumps(item_dict)}
            item_list.append(item)
        
        self.iterate_put_items(
            Creator.battey_swap_log['TableName'],
            item_list)

    def insert_vm_status(self, item_dict_list):
        item_list = []
        for item_dict in item_dict_list:
            item = {
                'Id': item_dict['vm_id'], 
                'Status': json.dumps(item_dict),
                'SnapTime': item_dict['snap_time']}
            item_list.append(item)
        
        self.iterate_put_items(
            Creator.vm_status['TableName'],
            item_list)
            
    def timestamp_to_dt_str(self, timestamp):
        '''
        Return a date_string and time_string by given timestamp
        '''
        dt_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return [dt_str[:10], dt_str[-8:]]

