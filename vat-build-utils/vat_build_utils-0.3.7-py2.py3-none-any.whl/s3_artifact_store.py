
import posixpath

import boto3
from botocore.exceptions import ClientError

class S3ArtifactStore(object):
    def __init__(self, config):
        self.bucket = config['bucket']
        self.prefix = config['prefix']

    def has_artifact(self, name, input_hash):
        s3 = boto3.client('s3')

        # Not so easy to check if an S3 object at a key exists
        try:
            obj = s3.head_object(Bucket=self.bucket, Key=self._get_artifact_key(name, input_hash))
            return True
        except ClientError as exc:
            if exc.response['Error']['Code'] != '404':
                raise
            else:
                return False

    def get_artifact_location(self, name, input_hash):
        # Not so easy to check if an S3 object at a key exists
        return {
            'type': 's3',
            'bucket': self.bucket,
            'key': self._get_artifact_key(name, input_hash)
        }

    def store_artifact_file(self, file_path, artifact_name, input_hash):
        s3 = boto3.resource('s3')

        artifact_object = s3.Object(self.bucket, self._get_artifact_key(artifact_name, input_hash))
        artifact_object.upload_file(file_path)

        return {
            'type': 's3',
            'bucket': self.bucket,
            'key': artifact_object.key
        }

    def store_artifact_fileobj(self, fileobj, artifact_name, input_hash):
        s3 = boto3.resource('s3')

        artifact_object = s3.Object(self.bucket, self._get_artifact_key(artifact_name, input_hash))
        artifact_object.upload_fileobj(fileobj)

        return {
            'type': 's3',
            'bucket': self.bucket,
            'key': artifact_object.key
        }

    def _get_artifact_key(self, artifact_name, input_hash):
        return posixpath.join(self.prefix, artifact_name, input_hash)
