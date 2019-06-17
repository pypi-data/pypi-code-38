from troposphere import Sub
from troposphere.iam import Policy
from ozone.filters.arns import (
    s3_bucket as filter_s3bucket,
    kms_key as filter_kmskey,
    kms_alias as filter_keyalias


def _allow_s3_replication_source_access(source_bucket):
    """
    Args:
        source_bucket: name or ARN of the source bucket for replication
    Returns:
        statement dict()
    """
    statement = {
        "Sid": "AllowObjectReplicationAccessFromSourceBucket",
        "Action": [
            "s3:ListBucket",
            "s3:GetReplicationConfiguration",
            "s3:GetObjectVersionForReplication",
            "s3:GetObjectVersionAcl",
            "s3:GetObjectVersionTagging"
        ],
        "Effect": "Allow",
        "Resource": [
            f'{source_bucket}',
            f'{source_bucket}/*'
        ]
    }
    return statement


def _allow_s3_replication_replica_access(replica_bucket, replica_key):
    """
    Args:
        replica_bucket: name or ARn of the replica bucket
    Returns:
        statement dict()
    """
    statement = {
        "Sid": "AllowObjectReplicationToReplicaBucket",
        "Action": [
            "s3:ReplicateObject",
            "s3:ReplicateDelete",
            "s3:ReplicateTags",
            "s3:GetObjectVersionTagging"
        ],
        "Effect": "Allow",
        "Condition": {
            "StringLikeIfExists": {
                "s3:x-amz-server-side-encryption": [
                    "aws:kms",
                    "AES256"
                ],
                "s3:x-amz-server-side-encryption-aws-kms-key-id": [
                    replica_key
                ]
            }
        },
        "Resource": f'{replica_bucket}/*'
    }
    return statement


def _allow_kms_decrypt_source(source_bucket, source_key):
    """
    Args:
        source_bucket: name or ARN of the source bucket for replication
        source_key: Key ID / ARN of the key used to decrypt source
    Returns:
        statement dict()
    """
    statement = {
        "Sid": "AllowKmsDecryptForObjectFromSourceBucket",
        "Action": [
            "kms:Decrypt"
        ],
        "Effect": "Allow",
        "Condition": {
            "StringLike": {
                "kms:ViaService": Sub("s3.${AWS::Region}.${AWS::URLSuffix}"),
                "kms:EncryptionContext:aws:s3:arn": [
                    f'{source_bucket}',
                    f'{source_bucket}/*'
                ]
            }
        },
        "Resource": [
            source_key
        ]
    }
    return statement


def _allow_kms_encrypt_replica(replica_bucket, replica_key):
    """
    Args:
        replica_bucket: name or ARN of the replica bucket for replication
        replica_key: Key ID / ARN of the key used to encrypt source
    Returns:
        statement dict()
    """
    statement = {
        "Sid": "AllowKmsEncryptForObjectToReplicaBucket",
        "Action": [
            "kms:Encrypt"
        ],
        "Effect": "Allow",
        "Condition": {
            "StringLike": {
                "kms:ViaService": Sub("s3.${ReplicaRegion}.${AWS::URLSuffix}"),
                "kms:EncryptionContext:aws:s3:arn": [
                    f'{replica_bucket}/*'
                ]
            }
        },
        "Resource": [
            replica_key
        ]
    }
    return statement


def iam_role_replica_with_kms(source_bucket, replica_bucket, source_key, replica_key):
    """
    Args:
        source_bucket: name/ARN of the source bucket
        replica_bucket: name/ARN of the replica bucket
        source_key: source_key ID or Alias for KMS encryption
        replica_key: key ID or Alias for KMS Encryption in the replica region
    Returns:
        policy Policy()
    """
    source_bucket = filter_s3bucket(source_bucket)
    replica_bucket = filter_s3bucket(replica_bucket)
    try:
        filter_replica_key = filter_kmskey(replica_key)
    except ValueError as error:
        pass
    try:
        filter_replica_key = filter_keyalias(replica_key)
    except:
        raise ValueError("Double failure")

    try:
        filter_source_key = filter_kmskey(source_key)
    except ValueError:
        pass
    try:
        filter_source_key = filter_keyalias(source_key)
    except ValueError:
        raise ValueError ("the KMS Key input is neither a valid Key ID or Key Alias")

    assert source_bucket
    assert replica_bucket
    statement = []
    statement.append(_allow_s3_replication_source_access(source_bucket))
    statement.append(_allow_s3_replication_replica_access(replica_bucket, filter_replica_key))
    statement.append(_allow_kms_decrypt_source(source_bucket, filter_source_key))
    statement.append(_allow_kms_encrypt_replica(replica_bucket, filter_replica_key))
    policy_doc = {
        "Version": "2012-10-17",
        "Statement": statement
    }
    policy = Policy(
        PolicyName="AllowBucketReplicationWithKmsEncryptDecrypt",
        PolicyDocument=policy_doc
    )
    return policy
