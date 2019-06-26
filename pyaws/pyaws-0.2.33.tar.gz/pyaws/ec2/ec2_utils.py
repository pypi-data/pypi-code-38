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
import subprocess
import inspect
import boto3
from botocore.exceptions import ClientError
from pyaws.session import boto3_session
from pyaws.core import loggers
from pyaws._version import __version__


# global objects
REGION = os.environ['AWS_DEFAULT_REGION']

# lambda custom log object
logger = loggers.getLogger(__version__)


# -- declarations -------------------------------------------------------------


def default_region(profile='default'):
    """
    Summary:
        Determines the default region of profilename present in the local awscli
        configuration or set in the environment via 'AWS_DEFAULT_REGION' variable.
        If all else fails, returns region code 'us-east-1' as a default region.
    Args:
        profile (str): profile_name of a valid profile from local awscli config
    Returns:
        AWS Region Code, TYPE str
    """

    stderr = ' 2>/dev/null'
    region = subprocess.getoutput(f'aws configure get profile.{profile}.region {stderr}')

    try:
        if region:
            return region
        elif os.getenv('AWS_DEFAULT_REGION') is None:
            os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    except Exception as e:
        logger.exception(
            f'{inspect.stack()[0][3]}: Unknown error while interrogating local awscli config: {e}'
            )
        raise
    return os.getenv('AWS_DEFAULT_REGION')


def get_instances(region, profile=None, pageSize=100):
    """
    Returns: all EC2 instance Ids in a region
    """
    ids = []
    try:
        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
            client = session.client('ec2')
        else:
            client = boto3.client('ec2', region_name=region)

        # find ebs volumes associated with instances
        paginator = client.get_paginator('describe_instances')
        response_iterator = paginator.paginate(PaginationConfig={'PageSize': pageSize})

        # collect all instances in region
        for page in response_iterator:
            # collect all instanceIds (not used)
            for x in [x[0]['InstanceId'] for x in [x['Instances'] for x in page['Reservations']]]:
                ids.append(x)

    except ClientError as e:
        logger.critical(
            "%s: problem retrieving instances in region %s (Code: %s Message: %s)" %
            (inspect.stack()[0][3], str(region), e.response['Error']['Code'],
            e.response['Error']['Message']))
        raise e
    return ids


def get_regions(profile=None):
    """ Return list of all regions """
    try:
        if profile is None:
            profile = 'default'
        client = boto3_session(service='ec2', profile=profile)

    except ClientError as e:
        logger.exception(
            '%s: Boto error while retrieving regions (%s)' %
            (inspect.stack()[0][3], str(e)))
        raise e
    return [x['RegionName'] for x in client.describe_regions()['Regions']]


def dns_hostname(instanceId, profile='default'):
    """
    Summary:
        Reverse DNS for EC2 instances public or private subnets
        Really only useful when EC2 instance assigned non-AWS DNS name
    Args:
        ip_info (dict):
            {
                "Association": {
                    "IpOwnerId": "102512488663",
                    "PublicDnsName": "ec2-34-247-23-51.eu-west-1.compute.amazonaws.com",
                    "PublicIp": "34.247.23.51"
                },
                "Primary": true,
                "PrivateDnsName": "ip-172-31-28-93.eu-west-1.compute.internal",
                "PrivateIpAddress": "172.31.28.93"
            }
    Returns:
        hostname (tuple): First element of the following tuple:
            (
                'ec2-34-247-23-51.eu-west-1.compute.amazonaws.com',
                ['34.247.23.51'],
                'ip-172-31-28-93.eu-west-1.compute.internal',
                ['172.31.28.93']
            )
    """
    try:
        session = boto3.Session(profile_name=profile)
        client = session.client('ec2', region_name=default_region(profile))
        r = client.describe_instances(InstanceIds=[instanceId])
        # dict of ip information
        ip_info = [x['PrivateIpAddresses'][0] for x in r['Reservations'][0]['Instances'][0]['NetworkInterfaces']][0]
        private_name = r['Reservations'][0]['Instances'][0]['PrivateDnsName']
        public_name = r['Reservations'][0]['Instances'][0]['PublicDnsName']

        """BELOW NEEDS DEBUGGING
        if ip_info.get('Association'):
            public_ip = ip_info['Association']['PublicIp']
            priv_ip = ip_info['PrivateIpAddress']
        else:
            public_ip = ''
            priv_ip = ip_info['PrivateIpAddress']
        return (
                socket.gethostbyaddr(public_ip),
                [public_ip],
                socket.gethostbyaddr(priv_ip),
                [priv_ip]
            )
        """
    except KeyError as e:
        logger.exception('%s: KeyError parsing ip info (%s)' % (inspect.stack()[0][3], str(e)))
        return ('', [], '', [])
    except ClientError as e:
        logger.exception('%s: Boto Error parsing ip info (%s)' % (inspect.stack()[0][3], str(e)))
        return ''
    except Exception:
        logger.exception(
            '%s: No dns info from reverse lookup - Unknown host' % inspect.stack()[0][3])
        return ('', [], '', [ip_info['PrivateIpAddress']])
    return public_name or private_name


def get_attached_ids(region, instanceId, profile=None):
    """
    Summary:
        Audits the entire namespace of an AWS Account (essentially an
        entire region) for resource ids of the type requested
    Args:
        instanceId (str): a single EC2 instance Identifier
        pageSize (int): paging is used,
    Returns:
        vids (str): ebs volume ids attached to instanceId
        enids (str): elastic network_interface ids attached to instanceId
    Raises:
        botocore ClientError
    """
    vids, eids = [], []

    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
        ec2 = session.resource('ec2')
    else:
        ec2 = boto3.resource('ec2', region_name=region)

    try:
        logger.info('%s:  function start' % inspect.stack()[0][3])

        base = ec2.instances.filter(InstanceIds=[instanceId])

        for instance in base:
            # get volume ids
            for vol in instance.volumes.all():
                vids.append(vol.id)
            # get network interfaces
            for eni in instance.network_interfaces:
                eids.append(eni.id)

            logger.info(
                    '%d volume(s), %d ENIs found for instance %s' %
                    (len(vids), len(eids), instanceId)
                )
    except ClientError as e:
        logger.exception(
            '%s: Problem while retrieving list of volumes for region %s' %
            (inspect.stack()[0][3], region))
        return [], []
    return vids, eids


def namespace_volumes_eids(region, profile=None, pageSize=200):
    """
    Summary:
        - Audits the entire namespace of an AWS Account (essentially an
          entire region) for resource ids of the type requested (with paging)
    Args:
        pageSize (int): paging is used,
    Returns:
        vids (str): ebs volume ids attached to instanceId
        enids (str): elastic network_interface ids attached to instanceId
    Raises:
        botocore ClientError
    """

    vids, enids = [], []

    try:
        logger.info('%s:  function start' % inspect.stack()[0][3])

        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
            client = session.client('ec2')
        else:
            client = boto3.client('ec2', region_name=region)

        # find ebs volumes associated with instances
        paginator = client.get_paginator('describe_volumes')
        response_iterator = paginator.paginate(PaginationConfig={'PageSize': pageSize})

        # collect all instances in region
        for page in response_iterator:
            # collect all instanceIds (not used)
            for z in [y['VolumeId'] for y in [x['Attachments'][0] for x in page['Volumes']]]:
                vids.append(z)

        logger.info('%d volume(s) found in region %s' % (len(vids), region))

        # find enis
        paginator = client.get_paginator('describe_network_interfaces')
        response_iterator = paginator.paginate(PaginationConfig={'PageSize': pageSize})

        # collect all instances in region
        for page in response_iterator:
            # collect all instanceIds (not used)
            for z in [x['NetworkInterfaceId'] for x in page['NetworkInterfaces']]:
                enids.append(z)

    except ClientError as e:
        logger.exception(
            '%s: Problem while retrieving list of volumes for region %s' %
            (inspect.stack()[0][3], REGION))
        return [], []
    return vids, enids
