"""
Generic Bucket build attempt
"""
from troposphere import (
    Sub
)
from troposphere.s3 import (
    Bucket,
    LifecycleConfiguration,
    LifecycleRule,
    VersioningConfiguration,
    AbortIncompleteMultipartUpload,
    BucketEncryption,
    SseKmsEncryptedObjects,
    SourceSelectionCriteria,
    ServerSideEncryptionRule,
    ServerSideEncryptionByDefault,
    ReplicationConfiguration,
    ReplicationConfigurationRules,
    ReplicationConfigurationRulesDestination,
    EncryptionConfiguration
)
from ozone.filters.arns import (
    s3_bucket as filter_s3bucket,
    iam_role as filter_role
)

S3_ARN = 'arn:aws:s3:::'

class S3Bucket(Bucket, object):


    def set_replication_rule(self, replica_bucket, **kwargs):
        """
        Args:
          replica_bucket: Name/ARN of the destination s3 bucket
        Returns:
          rule ReplicationConfigurationRule
        """
        replica_bucket_arn = filter_s3bucket(replica_bucket)
        destination = ReplicationConfigurationRulesDestination(
            Bucket=replica_bucket_arn
        )
        if 'UseEncryptionReplication' in kwargs.keys() and kwargs['UseEncryptionReplication']:
            encryption_config = EncryptionConfiguration(
                ReplicaKmsKeyID=kwargs['ReplicaKmsKeyID']
            )
            setattr(destination, 'EncryptionConfiguration', encryption_config)

        if 'ReplicateEncryptedObjects' in kwargs.keys() and kwargs['ReplicateEncryptedObjects']:
            source_criteria = SourceSelectionCriteria(
                SseKmsEncryptedObjects=SseKmsEncryptedObjects(
                    Status='Enabled'
                )
            )
        else:
            source_criteria = SourceSelectionCriteria(
                SseKmsEncryptedObjects=SseKmsEncryptedObjects(
                    Status='Disabled'
                )
            )
        rule = ReplicationConfigurationRules(
            Prefix='',
            Status='Enabled',
            Destination=destination,
            SourceSelectionCriteria=source_criteria
        )
        return rule


    def set_bucket_replication(self, **kwargs):
        """
        returns:
        bucket replication configuration
        """
        config = ReplicationConfiguration(
            Role=filter_role(kwargs['ReplicationRole']),
            Rules=[
                self.set_replication_rule(
                    kwargs['ReplicaBucket'],
                    **kwargs
                )
            ]
        )
        setattr(self, 'ReplicationConfiguration', config)


    def set_bucket_lifecycle(self):
        """
        returns:
        LifecycleConfiguration for S3Bucket
        """
        config = LifecycleConfiguration(
            Rules=[
                LifecycleRule(
                    Status='Enabled',
                    AbortIncompleteMultipartUpload=AbortIncompleteMultipartUpload(
                        DaysAfterInitiation=3
                    )
                )
            ]
        )
        setattr(self, 'LifecycleConfiguration', config)


    def set_bucket_encryption(self, **kwargs):
        """
        returns:
        EncryptionConfiguration for S3Bucket
        """
        if 'KMSMasterKeyID' in kwargs.keys():
            encryption_default = ServerSideEncryptionByDefault(
                SSEAlgorithm='aws:kms',
                KMSMasterKeyID=kwargs['KMSMasterKeyID']
            )
        else:
            encryption_default = ServerSideEncryptionByDefault(
                SSEAlgorithm='aws:kms'
            )
        config = BucketEncryption(
            ServerSideEncryptionConfiguration=[
                ServerSideEncryptionRule(
                    ServerSideEncryptionByDefault=encryption_default
                )
            ]
        )
        setattr(self, 'BucketEncryption', config)


    def __init__(self, title, bucket_name, **kwargs):
        """
        Args:
          kwargs:
            AppendRegion: boolean
            UseVersioning: boolean
            UseLifecycle: boolean

            UseReplication: boolean
            ReplicationRole: str() role name of full ARN
            ReplicaBucket: Name of the bucket for replication

            UseEncryptionReplication: boolean
            ReplicateEncryptedObjects: boolean (default true)
            ReplicaKmsKeyID: alias or arn of the KMS Key

            UseEncryption: boolean
            KMSMasterKeyID: Default KMS Key ID for encryption
        returns:
            S3Bucket
        """
        super().__init__(title)
        if 'AppendRegion' in kwargs.keys() and kwargs['AppendRegion']:
            self.BucketName = Sub(f'{bucket_name}-${{AWS::Region}}')
        else:
            self.BucketName = bucket_name
        if 'UseEncryption' in kwargs.keys() and kwargs['UseEncryption']:
            self.set_bucket_encryption(**kwargs)
        if 'UseLifecycle' in kwargs.keys() and kwargs['UseLifecycle']:
            self.set_bucket_lifecycle()
            if not hasattr(self, 'VersioningConfiguration'):
                setattr(
                    self, 'VersioningConfiguration',
                    VersioningConfiguration(
                        Status='Enabled'
                    )
                )
        if 'UseReplication' in kwargs.keys() and kwargs['UseReplication']:
            self.set_bucket_replication(**kwargs)
            if not hasattr(self, 'VersioningConfiguration'):
                setattr(
                    bucket, 'VersioningConfiguration',
                    VersioningConfiguration(
                        Status='Enabled'
                    )
                )


if __name__ == '__main__':
    import json
    print(json.dumps(
        S3Bucket(
            'test',
            UseEncryption=False,
            UseLifecycle=False,
            UseReplication=True,
            UseEncryptionReplication=False,
            ReplicationRole='arn:aws:iam:::role/toto',
            ReplicaBucket='destination-finale',
            KMSMasterKeyId=Sub('some-id-like-that'),
            ReplicaKmsKeyID=Sub('replica-key-id')
        ).to_dict(),
        indent=2
    ))
