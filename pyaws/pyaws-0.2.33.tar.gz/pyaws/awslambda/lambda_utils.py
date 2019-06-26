"""

lambda_utils (python3)

    Common functionality for use with AWS Lambda Service

Author:
    Blake Huber
    Copyright Blake Huber, All Rights Reserved.

License:

    MIT License.
    Additional terms may be found in the complete license agreement:
    https://opensource.org/licenses/MIT

    Project README:
    https://github.com/fstab50/pyaws/blob/master/README.md
"""


import os
import re
import json
import time
import inspect
import boto3
from botocore.exceptions import ClientError
from pyaws import logger


def get_account_info(account_profile=None):
    """
    Summary.

        Queries AWS iam and sts services to discover account id information
        in the form of account name and account alias (if assigned)

    Returns:
        TYPE: tuple

    Example usage:

    >>> account_number, account_name = lambda_utils.get_account_info()
    >>> print(account_number, account_name)
    103562488773 tooling-prod

    """
    if account_profile:
        session = boto3.Session(profile_name=account_profile)
        sts_client = session.client('sts')
        iam_client = session.client('iam')
    else:
        sts_client = boto3.client('sts')
        iam_client = boto3.client('iam')

    try:
        number = sts_client.get_caller_identity()['Account']
        name = iam_client.list_account_aliases()['AccountAliases'][0]

    except IndexError as e:
        name = '<no_alias_assigned>'
        logger.info('Error: %s. No account alias defined. account_name set to %s' % (e, name))
        return (number, name)
    except ClientError as e:
        logger.warning(
            "%s: problem retrieving caller identity (Code: %s Message: %s)" %
            (inspect.stack()[0][3], e.response['Error']['Code'], e.response['Error']['Message'])
            )
        raise e
    return (number, name)


def get_regions():
    """
    Summary.

        Returns list of region codes for all AWS regions worldwide

    Returns:
        TYPE: list

    """
    try:
        client = boto3.client('ec2')
        region_response = client.describe_regions()
        regions = [region['RegionName'] for region in region_response['Regions']]

    except ClientError as e:
        logger.critical(
            "%s: problem retrieving aws regions (Code: %s Message: %s)" %
            (inspect.stack()[0][3], e.response['Error']['Code'],
            e.response['Error']['Message']))
        raise e
    return regions


def sns_notification(topic_arn, subject, message, account_id=None, account_name=None):
    """
    Summary.

        Sends message to AWS sns service topic provided as a
        parameter

    Args:
        topic_arn (str): sns topic arn
        subject (str): subject of sns message notification
        message (str): message body

    Returns:
        TYPE: Boolean | Success or Failure

    """
    if not (account_id or account_name):
        account_id, account_name = get_account_info()

    # assemble msg
    header = 'AWS Account: %s (%s) | %s' % \
        (str(account_name).upper(), str(account_id), subject)
    msg = '\n%s\n\n%s' % (time.strftime('%c'), message)
    msg_dict = {'default': msg}

    # client
    region = (topic_arn.split('sns:', 1)[1]).split(":", 1)[0]
    client = boto3.client('sns', region_name=region)

    try:
        # sns publish
        response = client.publish(
            TopicArn=topic_arn,
            Subject=header,
            Message=json.dumps(msg_dict),
            MessageStructure='json'
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == '200':
            return True
        else:
            return False
    except ClientError as e:
        logger.exception(
            '%s: problem sending sns msg (Code: %s Message: %s)' %
            (inspect.stack()[0][3], e.response['Error']['Code'],
                e.response['Error']['Message']))
        return False
