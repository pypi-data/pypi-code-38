"""
Summary:
    ec2_utils (python3) | Common EC2 functionality implemented by boto3 SDK

Author:
    Blake Huber
    Copyright Blake Huber, All Rights Reserved.

License:
    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee is hereby granted,
    provided that the above copyright notice appear in all copies and that
    both the copyright notice and this permission notice appear in
    supporting documentation

    Additional terms may be found in the complete license agreement located at:
    https://bitbucket.org/blakeca00/lambda-library-python/src/master/LICENSE.md

"""
import os
import inspect
import boto3
from botocore.exceptions import ClientError, ProfileNotFound
from pyaws.utils import stdout_message
from pyaws import logger


# global objects
REGION = os.environ['AWS_DEFAULT_REGION']


# -- declarations -------------------------------------------------------------


def running_instances(region, profile=None, ids=False, debug=False):
    """
    Summary.
        Determines state of all ec2 machines in a region

    Returns:
        :running ec2 instances, TYPE: ec2 objects
            OR
        :running ec2 instance ids, TYPE: str
    """
    try:
        if profile and profile != 'default':
            session = boto3.Session(profile_name=profile)
            ec2 = session.resource('ec2', region_name=region)
        else:
            ec2 = boto3.resource('ec2', region_name=region)

        instances = ec2.instances.all()

        if ids:
            return [x.id for x in instances if x.state['Name'] == 'running']

    except ClientError as e:
        logger.exception(
            "%s: IAM user or role not found (Code: %s Message: %s)" %
            (inspect.stack()[0][3], e.response['Error']['Code'],
             e.response['Error']['Message']))
        raise
    except ProfileNotFound:
        msg = (
            '%s: The profile (%s) was not found in your local config' %
            (inspect.stack()[0][3], profile))
        stdout_message(msg, 'FAIL')
        logger.warning(msg)
    return [x for x in instances if x.state['Name'] == 'running']


def stopped_instances(region, profile=None, ids=False, debug=False):
    """
    Summary.
        Determines state of all ec2 machines in a region

    Returns:
        :stopped ec2 instances, TYPE: ec2 objects
            OR
        :stopped ec2 instance ids, TYPE: str

    """
    try:
        if profile and profile != 'default':
            session = boto3.Session(profile_name=profile)
            ec2 = session.resource('ec2', region_name=region)
        else:
            ec2 = boto3.resource('ec2', region_name=region)

        instances = ec2.instances.all()

        if ids:
            return [x.id for x in instances if x.state['Name'] == 'stopped']

    except ClientError as e:
        logger.exception(
            "%s: IAM user or role not found (Code: %s Message: %s)" %
            (inspect.stack()[0][3], e.response['Error']['Code'],
             e.response['Error']['Message']))
        raise
    except ProfileNotFound:
        msg = (
            '%s: The profile (%s) was not found in your local config' %
            (inspect.stack()[0][3], profile))
        stdout_message(msg, 'FAIL')
        logger.warning(msg)
    return [x for x in instances if x.state['Name'] == 'stopped']
