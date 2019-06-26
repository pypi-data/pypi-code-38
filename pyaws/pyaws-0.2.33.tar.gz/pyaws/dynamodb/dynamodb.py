"""
Summary:
    Boto3 DynamoDB Reader Operations

"""

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from pyaws import logger


class DynamoDBReader():
    def __init__(self, aws_account_id, service_role, tablename, region):
        """
        Reads DynamoDB table
        """
        self.tablename = tablename
        self.region = region
        self.aws_account_id = aws_account_id
        self.service_role = service_role
        self.aws_credentials = self.assume_role(aws_account_id, service_role)


    def boto_dynamodb_resource(self, region):
        """
        Initiates boto resource to communicate with AWS API
        """
        try:
            dynamodb_resource = boto3.resource(
                'dynamodb',
                aws_access_key_id=self.aws_credentials['AccessKeyId'],
                aws_secret_access_key=self.aws_credentials['SecretAccessKey'],
                aws_session_token=self.aws_credentials['SessionToken'],
                region_name=region
            )
        except ClientError as e:
            logger.exception("Unknown problem creating boto3 resource (Code: %s Message: %s)" %
                    (e.response['Error']['Code'], e.response['Error']['Message']))
            return 1
        return dynamodb_resource

    def assume_role(self, aws_account_id, service_role):
        """
        Summary.

            Assumes a DynamoDB role in 'destination' AWS account

        Args:
            aws_account_id (str): 12 digit AWS Account number containing dynamodb table
            service_role (str):  IAM role dynamodb service containing permissions
                allowing interaction with dynamodb

        Returns:
            temporary credentials for service_role when assumed, TYPE: json
        """
        session = boto3.Session()
        sts_client = session.client('sts')

        try:

            # assume role in destination account
            assumed_role = sts_client.assume_role(
                    RoleArn="arn:aws:iam::%s:role/%s" % (str(aws_account_id), service_role),
                    RoleSessionName="DynamoDBReaderSession"
                )

        except ClientError as e:
            logger.exception(
                "Couldn't assume role to read DynamoDB, account " +
                str(aws_account_id) + " (switching role) (Code: %s Message: %s)" %
                (e.response['Error']['Code'], e.response['Error']['Message']))
            raise e
        return assumed_role['Credentials']

    def query_dynamodb(self, partition_key, key_value):
        """
        Queries DynamoDB table using partition key,
        returns the item matching key value
        """
        try:
            resource_dynamodb = self.boto_dynamodb_resource(self.region)
            table = resource_dynamodb.Table(self.tablename)
            logger.info('Table %s: Table Item Count is: %s' % (table.table_name, table.item_count))

            # query on parition key
            response = table.query(KeyConditionExpression=Key(partition_key).eq(str(key_value)))
            if response['Items']:
                item = response['Items'][0]['Account Name']
            else:
                item = 'unIdentified'

        except ClientError as e:
            logger.exception("Couldn\'t query DynamoDB table (Code: %s Message: %s)" %
                (e.response['Error']['Code'], e.response['Error']['Message']))
            return 1
        return item

    def scan_accounts(self, account_type):
        """
        Read method for DynamoDB table
        """

        accounts, account_ids = [], []
        valid_mpc_pkgs = ['B', 'RA-PKG-B', 'RA-PKG-C', 'P', 'ATA', 'BUP', 'DXA']

        types = [x.strip(' ') for x in account_type.split(',')]    # parse types

        try:
            resource_dynamodb = self.boto_dynamodb_resource(self.region)
            table = resource_dynamodb.Table(self.tablename)
            # scan table
            if set(types).issubset(set(valid_mpc_pkgs)):
                for type in types:
                    response = table.scan(FilterExpression=Attr('MPCPackage').eq(type))
                    for account_dict in response['Items']:
                        accounts.append(account_dict)
            elif types[0] == 'All':
                # all valid_mpc_pkgs accounts (commercial accounts)
                response = table.scan(FilterExpression=Attr('MPCPackage').ne("P"))
                for account_dict in response['Items']:
                    accounts.append(account_dict)

        except ClientError as e:
            logger.exception("Couldn\'t scan DynamoDB table (Code: %s Message: %s)" %
                    (e.response['Error']['Code'], e.response['Error']['Message']))
            return 1

        if accounts:
            for account in accounts:
                account_info = {}
                account_info['AccountName'] = account['Account Name']
                account_info['AccountId'] = account['Account ID']
                account_ids.append(account_info)
        else:
            logger.info('No items returned from DyanamoDB')
        return account_ids
