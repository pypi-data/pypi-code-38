import boto3

from metagenomi.config import AWS_CONFIG
from metagenomi.logger import logger


class Dbconn(object):
    def __init__(self,
                 regionname=AWS_CONFIG['REGION'],
                 tablename=AWS_CONFIG['DYNAMODB_TABLE_NAME']):
        try:
            dynamodb = boto3.resource('dynamodb', region_name=regionname)
            logger.info(f"Connected to dynamodb in region {regionname}")

            self.table = dynamodb.Table(tablename)
            logger.info(f"Using dynamodb table {tablename}")

        except Exception as e:
            e = (f'Could not connect to dynamodb. Check config and db {e}')
            logger.critical(e)
            raise ValueError(e)


S3 = boto3.client('s3')
S3resource = boto3.resource('s3')

dbconn = Dbconn(regionname=AWS_CONFIG['REGION'],
                tablename=AWS_CONFIG['DYNAMODB_TABLE_NAME'])

testdb = Dbconn(regionname=AWS_CONFIG['REGION'],
                tablename='mg-test')

olddb = Dbconn(regionname=AWS_CONFIG['REGION'],
               tablename='mg-project-metadata')

hmmdb = Dbconn(regionname=AWS_CONFIG['REGION'],
               tablename=AWS_CONFIG['HMM_TABLE_NAME'])

spacer_hit_db = Dbconn(regionname=AWS_CONFIG['REGION'],
                       tablename=AWS_CONFIG['SPACER_HIT_TABLE_NAME'])


batch_client = boto3.client('batch', region_name=AWS_CONFIG['REGION'])
