import boto3
import configparser

class DynamoDBDataHelper():

    def __init__(
        self, 
        logger=None,
        config_file='go_servers.ini',
        host_name='ML_Learning_DEV'):
        self.logger = logger
        self.config_file = config_file
        self.host_name = host_name
        self.connect()

    def connect(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        self.dynamodb = boto3.client(
            'dynamodb',
            region_name=self.config[self.host_name]['REGION'])

    def get_table(self, table_name):
        return boto3.resource(
                'dynamodb',
                region_name=self.config[self.host_name]['REGION']).Table(table_name)

    def create_table(self, table_dict):
        table = self.dynamodb.create_table(
            AttributeDefinitions=table_dict['AttributeDefinitions'],
            TableName=table_dict['TableName'],
            KeySchema=table_dict['KeySchema'],
            ProvisionedThroughput=table_dict['ProvisionedThroughput']
        )

        if self.logger != None:
            self.logger.info('Create Table: %s' % table)
        
        return table

    def update_table(self, table_dict):
        table = self.dynamodb.update_table(
            AttributeDefinitions=table_dict['AttributeDefinitions'],
            TableName=table_dict['TableName'],
            #KeySchema=table_dict['KeySchema'],
            ProvisionedThroughput=table_dict['ProvisionedThroughput']
        )

        if self.logger != None:
            self.logger.info('Update Table: %s' % table)
        
        return table

    def delete_table(self, table_name):
        table = self.dynamodb.delete_table(
            TableName=table_name
        )

        if self.logger != None:
            self.logger.info('Delete Table: %s' % table)

        return table
    
    def get_table_metadata(table_name):
        """
         Get some metadata about chosen table.
        """
        table = self.get_table(table_name)

        return {
            'num_items': table.item_count,
            'primary_key_name': table.key_schema[0],
            'status': table.table_status,
            'bytes_size': table.table_size_bytes,
            'global_secondary_indices': table.global_secondary_indexes
        }

    def query_table(self, table_name, filter_key=None, filter_value=None):
        """
        Perform a query operation on the table. 
        Can specify filter_key (col name) and its value to be filtered.
        """
        table = self.get_table(table_name)

        if self.logger != None:
            self.logger.info('Query Table %s with Key=%s and value=%s: %s' % (table, filter_key, filter_value))


        if filter_key and filter_value:
            filtering_exp = Key(filter_key).eq(filter_value)
            #Key(filter_key).
            data = table.query(KeyConditionExpression=filtering_exp)
        else:
            data = table.query()

        if self.logger != None:
            self.logger.info('Query Table with Key=%s and value=%s: %s' % (filter_key, filter_value, table))
            self.logger_info('result.count = %s' % len(data))
            if len(result) > 0:
                self.logger_info('result[0] = %s' % data[0])

        return data

    '''
    Put item: {'ResponseMetadata': {'HTTPHeaders': {'x-amz-crc32': '2745614147', 'connection': 'keep-alive', 'server': 'Server', 'date': 'Fri, 07 Dec 2018 07:24:58 GMT', 'x-amzn-requestid': 'F3RRH4E1QA0IV4B1D0SCCMAELFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2'}, 'RetryAttempts': 0, 'RequestId': 'F3RRH4E1QA0IV4B1D0SCCMAELFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200}}
    '''
    def put_item(self, table_name, item_dict):
        table = self.get_table(table_name)
        response = table.put_item(
            TableName=table_name,
            Item=item_dict
        )
        
        if self.logger != None:
            self.logger.info('Put item to Table %s with response = %s' % (table_name, response))

        return response

    def iterate_put_items(self, table_name, item_dict_list):
        table = self.get_table(table_name)

        if self.logger != None:
            self.logger.info('Iteratively put %s items to Table %s' % (len(item_dict_list), table_name))

        response = ''
        for item_dict in item_dict_list:
            response = table.put_item(
                TableName=table_name,
                Item=item_dict
            )
            if self.logger != None and response['ResponseMetadata']['HTTPStatusCode']!=200:
                self.logger.warn('Put item unsuccessfully with item = %s and response = %s' % (item_dict, response))

        if self.logger != None:
             self.logger.info('Put last item with response = %s' % response)

        return response
