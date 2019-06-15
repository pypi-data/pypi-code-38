from datetime import datetime

import boto3

from cheapodb import logger
from cheapodb.database import Database


class Schema(object):
    def __init__(self, name: str, db: Database):
        """
        Represents a prefix in an S3 bucket that models a database schema

        :param name: name of the schema to be created
        :param db: a CheapoDB Database object
        """
        self.name = name
        self.db = db
        self.glue = boto3.client('glue')
        self.crawler = self.create_crawler()

    def create_crawler(self):
        logger.info(f'Creating crawler {self.name}')
        try:
            payload = dict(
                Name=self.name,
                Role=self.db.iam_role_arn,
                DatabaseName=self.db.name,
                Description=f'Crawler created by CheapoDB on {datetime.now():%Y-%m-%d %H:%M:%S}',
                Targets=dict(
                    S3Targets=[
                        {
                            'Path': f'{self.db.name}/{self.name}'
                        }
                    ]
                )
            )
            self.glue.create_crawler(**payload)
            response = self.glue.get_crawler(
                Name=self.name
            )
            return response['Crawler']['Name']
        except self.glue.exceptions.AlreadyExistsException:
            logger.warning(f'Crawler {self.name} already existed')
            response = self.glue.get_crawler(
                Name=self.name
            )
            return response['Crawler']['Name']

    def delete_crawler(self, name):
        pass

    def update_tables(self, wait=False):
        response = self.glue.start_crawler(
            Name=self.crawler
        )
        if wait:
            pass
