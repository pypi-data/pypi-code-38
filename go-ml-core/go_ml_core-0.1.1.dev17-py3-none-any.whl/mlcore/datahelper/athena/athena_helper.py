import boto3
import botocore
import random

import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

class AthenaHelper():

    def __init__(self, config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.connect()

    def connect(self):
        ###################################################
        '''
        return athena resource
        '''
        def get_athena_resource(config):
            if 'role-arn' in config and config['role-arn']!='':
                if 'aws-access-key-id' in config and 'aws-secret-access-key' in config:
                    sts_client = boto3.client(
                        'sts',
                        aws_access_key_id=config['aws-access-key-id'],
                        aws_secret_access_key=config['aws-secret-access-key'],
                        region_name=config['region'])
                else:
                    sts_client = boto3.client('sts')

                session_name = '%s-%s'%(config['role-session-name'], str(random.randint(1,100)))
                #self.logger.info('session_name = %s' % session_name)
                assumed_role_object = sts_client.assume_role(
				    RoleArn=config['role-arn'],
				    RoleSessionName=session_name)
                credentials = assumed_role_object['Credentials']
            
                athena = boto3.client(
				    'athena',
				    aws_access_key_id=credentials['AccessKeyId'],
				    aws_secret_access_key=credentials['SecretAccessKey'],
				    aws_session_token=credentials['SessionToken'],
                    region_name=config['region'])
            else:
                if 'aws-access-key-id' in config and 'aws-secret-access-key' in config:
                    athena = boto3.client(
                        'athena',
                        aws_access_key_id=config['aws-access-key-id'],
                        aws_secret_access_key=config['aws-secret-access-key'],
                        region_name=config['region'])
                else:
                    athena = boto3.client(
                        'athena',
                        region_name=config['region'])

            return {
                'athena': athena,
                's3output': config['s3output'],
            }
        ###################################################
        
        self.athena = get_athena_resource(self.config)

    def run_query(self, query, database):
        self.connect()
        query_response = self.athena['athena'].start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': database
            },
            ResultConfiguration={
                'OutputLocation': self.athena['s3output'],
            }
        )
        return query_response

    def create_db(self, database):
        self.connect()
        query_create_db = '''
CREATE DATABASE IF NOT EXISTS %s
        ''' % (database)
        query_response = self.athena['athena'].start_query_execution(
            QueryString=query_create_db,
            ResultConfiguration={
                'OutputLocation': self.athena['s3output']
            }
        )
        self.logger.info('Create database result is shown in %s%s.txt' % (self.athena['s3output'], query_response['QueryExecutionId']))
        return query_response

    def query(self, query, database):
        self.logger.info('Run query %s (database=%s)' % (query, database))
        query_response = self.run_query(query, database)
        self.logger.info('Query result is shown in %s%s.txt' % (self.athena['s3output'], query_response['QueryExecutionId']))
        return query_response
        
    def drop_table(self, table, database):
        query_drop_table = '''
DROP TABLE %s.%s
        ''' % (database, table)
        self.logger.info('Drop table %s (database=%s)' % (table, database))
        query_response = self.run_query(query_drop_table, database)
        self.logger.info('Drop table result is shown in %s%s.txt' % (self.athena['s3output'], query_response['QueryExecutionId']))
        return query_response





