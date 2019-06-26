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
import datetime
import inspect
import boto3
from botocore.exceptions import ClientError
from pyaws import logd, __version__


# global objects


# lambda custom log object
logger = logd.getLogger(__version__)


# -- declarations -------------------------------------------------------------


def snapshot_metadata(snapshot_id, region, tags=False, profile=None):
    """
    Creates EC2 Snapshot Object to extract detailed metadata
    Returns:
        metadata (TYPE dict) | contains snapshot attribute values
    """
    metadata = {}
    try:
        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
            ec2 = session.resource('ec2')
        else:
            ec2 = boto3.resource('ec2', region_name=region)
        snapshot_obj = ec2.Snapshot(snapshot_id)
        metadata = {
                'SnapshotId': snapshot_id,
                'State': snapshot_obj.state,
                'Description': snapshot_obj.description,
                'Encrypted': snapshot_obj.encrypted,
                'KmsKeyId': snapshot_obj.kms_key_id,
                'VolumeId': snapshot_obj.volume_id,
                'VolumeSize': snapshot_obj.volume_size,
                'StartTime': snapshot_obj.start_time,
                'ProgressPct': snapshot_obj.progress.split('%')[0],
                'OwnerId': snapshot_obj.owner_id
            }
        if tags:
            metadata['Tags'] = snapshot_obj.tags
    except ClientError as e:
        logger.critical(
            "%s: problem retrieving metadata for snapshot %s (Code: %s Message: %s)" %
            (inspect.stack()[0][3], snapshot_id, e.response['Error']['Code'],
            e.response['Error']['Message']))
        raise e
    return metadata


class SnapshotOperations():
    """
    Summary:
        EC2 Snapshot Operations Class: List, Create, Delete, CreateVolume
    """
    def __init__(self, region, profile=None):
        self.snapshot_list = []
        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
            self.client = session.client('ec2')
            self.sts_client = session.client('sts')
        else:
            self.client = boto3.client('ec2', region_name=region)
            self.sts_client = boto3.client('sts', region_name=region)
        self.acct_number = self.sts_client.get_caller_identity()['Account']

    def list(self, account=None, volume_ids=None):
        """
        Args:
            AWS Account (str)
        Returns:
            List (TYPE list): all snapshots in region owned by account
                Works for large numbers of snapshots (pagination)
        """
        if not account:
            account = self.acct_number
        try:
            paginator = self.client.get_paginator('describe_snapshots')

            if volume_ids:
                response_iterator = paginator.paginate(
                        Filters=[
                            {
                                'Name': 'volume-id',
                                'Values': volume_ids
                            },
                        ],
                        PaginationConfig={'PageSize': 100}
                    )
            else:
                response_iterator = paginator.paginate(
                        OwnerIds=[str(account)],
                        PaginationConfig={'PageSize': 100}
                    )
            # page thru, retrieve all snapshots
            snapshot_ids, temp = [], []
            for page in response_iterator:
                temp = [x['SnapshotId'] for x in page['Snapshots']]
                for pageid in temp:
                    if pageid not in snapshot_ids:
                        snapshot_ids.append(pageid)
            # persist at the instance level for future use
            self.snapshot_list = [x for x in snapshot_ids]
        except ClientError as e:
            logger.critical(
                "%s: Problem during snapshot retrieval operation (Code: %s Message: %s)" %
                (inspect.stack()[0][3], e.response['Error']['Code'],
                 e.response['Error']['Message']))
            raise e
        return snapshot_ids

    def create(self, volume_list):
        """
        Returns:
            :result (dict): {'SnapshotID': 'State'}
        """
        result, snap_dict = [], {}
        now = datetime.datetime.utcnow()
        try:
            for vol_id in volume_list:
                now = now + datetime.timedelta(seconds=1)
                description = 'Snap Date: ' + str(now.strftime("%Y-%m-%dT%H:%M:%SZ"))
                r = self.client.create_snapshot(
                        VolumeId=vol_id,
                        Description=description
                    )
                logger.info(
                    'Created snapshot %s from volume %s' % (r['SnapshotId'], vol_id)
                    )
                result.append(
                        {r['SnapshotId']: r['State'], 'Description': description}
                    )
        except ClientError as e:
            logger.critical(
                "%s: Problem creating snapshot from volume %s (Code: %s Message: %s)" %
                (inspect.stack()[0][3], vol_id, e.response['Error']['Code'],
                e.response['Error']['Message']))
            raise e
        return result

    def delete(self, snapshot_list):
        """
        Args:
            snapshot_list (list):  list of snapshot ids
        Returns:
             :result (dict): {'SnapshotID': 'State'}
        """
        result = []
        try:
            for snapshot_id in snapshot_list:
                r = self.client.delete_snapshot(SnapshotId=snapshot_id)
                logger.info('Deleted snapshot %s' % str(snapshot_id))
                result.append(
                    {
                        'SnapshotId': snapshot_id,
                        'HTTPStatusCode': r['ResponseMetadata']['HTTPStatusCode']
                    }
                )
        except ClientError as e:
            logger.critical(
                "%s: Problem deleting snapshot %s (Code: %s Message: %s)" %
                (inspect.stack()[0][3], snapshot_id, e.response['Error']['Code'],
                e.response['Error']['Message']))
            raise e
        return result

    def create_volume(self, snapshot_id,  az, vol_type='gp2',
                            size=None, encrypted=False, kms_key=''):
        """
        Summary:
            Creates new ebs volume from snapshot(s)
        Args:
            - snapshot_id (str, required)
            - az (str, required): Availability Zone in which to create volume
            - vol_type (str):  'standard', 'gp2', 'io2',
            - size (str): Size in GB, required only if larger than orig volume size
            - encrypted (bool)
            - kms_key (str): KMS key id (required if encrypted = True)
        Returns:
             :result (dict)
        """
        try:
            r = self.client.create_volume(
                    SnapshotId=snapshot_id,
                    Size=size,
                    VolumeType=vol_type,
                    KmsKeyId=kms_key,
                    Encrypted=encrypted
                )
            logger.info(
                'Creating volume %s from snapshot %s' % (r['VolumeId'], snapshot_id)
                )
        except ClientError as e:
            logger.critical(
                "%s: Problem creating volume from snapshot %s (Code: %s Message: %s)" %
                (inspect.stack()[0][3], snapshot_id, e.response['Error']['Code'],
                e.response['Error']['Message']))
            raise e
        return {
                 'VolumeId': r['VolumeId'],
                 'State': r['State'],
                 'Source': snapshot_id,
                 'Encrypted': encrypted
               }
