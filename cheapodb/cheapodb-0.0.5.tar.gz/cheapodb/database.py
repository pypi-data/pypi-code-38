import os
import json
import time
import logging
from datetime import datetime
from typing import Union

import boto3
from pyathena import connect
from pyathena.cursor import Cursor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S'
)

logger = logging.getLogger(__name__)


class Database(object):
    def __init__(self, name: str, description: str = None, auto_create=False, results_prefix='results/',
                 create_iam_role=True, iam_role_name=None, **kwargs):
        self.name = name
        self.description = description
        self.auto_create = auto_create
        self.results_prefix = results_prefix
        self.create_iam_role = create_iam_role
        self.iam_role_name = iam_role_name

        self.session = boto3.session.Session(
            region_name=kwargs.get('aws_default_region', os.getenv('AWS_DEFAULT_REGION')),
            aws_access_key_id=kwargs.get('aws_access_key_id', os.getenv('AWS_ACCESS_KEY_ID')),
            aws_secret_access_key=kwargs.get('aws_secret_access_key', os.getenv('AWS_SECRET_ACCESS_KEY'))
        )
        self.s3 = self.session.resource('s3')
        self.glue = self.session.client('glue')
        iam = self.session.client('iam')

        self.bucket = self.s3.Bucket(self.name)

        if self.create_iam_role and not self.iam_role_name:
            self.iam_role_name = f'{self.name}-CheapoDBExecutionRole'
            try:
                response = iam.create_role(
                    RoleName=self.iam_role_name,
                    Path='/service-role/',
                    Description=f'IAM role created by CheapoDB on {datetime.now():%Y-%m-%d %H:%M:%S}',
                    AssumeRolePolicyDocument=json.dumps(dict(
                        Version='2012-10-17',
                        Statement=[
                            {
                                'Sid': '',
                                'Effect': 'Allow',
                                'Principal': {
                                    'Service': 'glue.amazonaws.com'
                                },
                                'Action': 'sts:AssumeRole'
                            }
                        ]
                    ))
                )
                self.iam_role_arn = response['Role']['Arn']

                response = iam.attach_role_policy(
                    RoleName=self.iam_role_name,
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole'
                )
                logger.debug(response)

                response = iam.put_role_policy(
                    RoleName=self.iam_role_name,
                    PolicyName='CheapoDBRolePolicy',
                    PolicyDocument=json.dumps(dict(
                        Version='2012-10-17',
                        Statement=[
                            {
                                'Effect': 'Allow',
                                'Action': [
                                    's3:GetObject',
                                    's3:PutObject'
                                ],
                                'Resource': [
                                    f'arn:aws:s3:::{self.name}*'
                                ]
                            }
                        ]
                    ))
                )
                logger.debug(response)
            except iam.exceptions.EntityAlreadyExistsException:
                logger.debug(f'Role already exists for database: CheapoDBRole-{self.name}')
                response = iam.get_role(
                    RoleName=self.iam_role_name
                )
                self.iam_role_arn = response['Role']['Arn']
        elif self.iam_role_name:
            response = iam.get_role(
                RoleName=self.iam_role_name
            )
            self.iam_role_arn = response['Role']['Arn']

        if self.auto_create:
            self.create()

    def create(self, ) -> dict:
        logger.info(f'Creating database {self.name} in {self.session.region_name}')

        bucket_params = dict(
            CreateBucketConfiguration=dict(
                LocationConstraint=self.session.region_name
            )
        )
        response = self.bucket.create(**bucket_params)
        logger.debug(response)

        db_params = dict(Name=self.name)
        if self.description:
            db_params['Description'] = self.description
        self.glue.create_database(
            DatabaseInput=db_params
        )
        return response

    def query(self, sql: str, results_path: str = None) -> dict:
        """
        Execute a query

        :param sql: the Athena-compliant SQL to execute
        :param results_path: optional S3 path to write results. Defaults to current DB bucket and
        instance results_prefix
        :return:
        """
        if not results_path:
            results_path = f's3://{self.bucket.name}/{self.results_prefix}'

        cursor = self.export(sql, results_path)
        columns = [column[0] for column in cursor.description]
        logger.info(cursor.description)
        for row in cursor:
            yield dict(zip(columns, row))

    def export(self, sql: str, results_path: str) -> Cursor:
        """
        Execute a query and return the cursor

        :param sql: the Athena-compliant SQL to execute
        :param results_path: required S3 path to write export
        :return: a pyathena cursor object
        """
        cursor = connect(
            s3_staging_dir=results_path,
            region_name=self.session.region_name
        ).cursor()
        cursor.execute(sql)
        return cursor

    def create_crawler(self, name, schedule: str = None, table_prefix: str = None, update_behavior='UPDATE_IN_DATABASE',
                       delete_behavior='DELETE_FROM_DATABASE') -> str:
        """
        Create a new Glue crawler.

        Either loads a crawler or creates it if it doesn't exist. The provided name of the crawler
        corresponds to the prefix of the DB bucket it will target.

        :param name: the DB bucket prefix to crawl
        :param schedule: an optional schedule in cron syntax to run the crawler
        :param table_prefix: an optional prefix to apply to the created tables
        :param update_behavior: how the crawler should handle schema updates
        :param delete_behavior: how the crawler should handle deletions
        :return: the name of the created crawler
        """
        try:
            logger.debug(f'Creating crawler {name}')
            payload = dict(
                Name=name,
                Role=self.iam_role_arn,
                DatabaseName=self.name,
                Description=f'Crawler created by CheapoDB on {datetime.now():%Y-%m-%d %H:%M:%S}',
                Targets=dict(
                    S3Targets=[
                        {
                            'Path': f'{self.name}/{name}/'
                        }
                    ]
                ),
                TablePrefix=table_prefix,
                SchemaChangePolicy={
                    'UpdateBehavior': update_behavior,
                    'DeleteBehavior': delete_behavior
                }
            )
            if schedule:
                payload['Schedule'] = schedule
            self.glue.create_crawler(**payload)
            return self.glue.get_crawler(Name=name)['Crawler']['Name']
        except self.glue.exceptions.AlreadyExistsException:
            logger.debug(f'Crawler {name} already exists')
            return self.glue.get_crawler(Name=name)['Crawler']['Name']

    def update_tables(self, crawler, wait: Union[bool, int] = 60) -> None:
        logger.info(f'Updating tables with crawler {crawler}')
        response = self.glue.start_crawler(
            Name=crawler
        )
        logger.debug(response)
        if wait:
            logger.info(f'Waiting for table update to complete...')
            while True:
                response = self.glue.get_crawler(Name=crawler)
                elapsed = response['Crawler']['CrawlElapsedTime'] / 1000
                if response['Crawler']['State'] == 'RUNNING':
                    logger.debug(response)
                    logger.info(f'Crawler in RUNNING state. Elapsed time: {elapsed} secs')
                    time.sleep(wait)
                    continue
                elif response['Crawler']['State'] == 'STOPPING':
                    logger.debug(response)
                    logger.info(f'Crawler in STOPPING state')
                    time.sleep(wait)
                    continue
                else:
                    status = response['Crawler']['LastCrawl']['Status']
                    logger.debug(response)
                    logger.info(f'Crawler in READY state. Table update {status}')
                    break

        return
