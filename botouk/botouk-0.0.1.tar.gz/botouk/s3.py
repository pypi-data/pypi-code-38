# -*- coding: utf-8 -*-
import os

from .base import Service, ResourceMixIn

from logging import getLogger

logger = getLogger(__name__)


class S3(Service, ResourceMixIn):
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
    """
    service_name = 's3'

    def __init__(self, session=None):
        super().__init__(session)

    def bucket(self, bucket_name):
        return self.resource.Bucket(bucket_name)

    def download_file(self, bucket, key, filename, **kwargs):
        return self.bucket(bucket) \
            .download_file(Key=key, Filename=filename, **kwargs)

    def list_objects(self, bucket, **kwargs):
        class Content:
            def __init__(self, content):
                self.key = content['Key']
                self.last_modified = content['LastModified']
                self.etag = content['ETag']
                self.size = content['Size']
                self.storage_class = content['StorageClass']

            def __str__(self):
                return self.key

            def __repr__(self):
                return self.__str__()

        class Response:
            def __init__(self, response):
                self.body = response
                self.metadata = response['ResponseMetadata']
                self.is_truncated = response['IsTruncated']
                self.contents = [Content(c) for c in response['Contents']]
                self.name = response['Name']
                self.prefix = response['Prefix']
                self.key_count = response['KeyCount']

            @property
            def files(self):
                return [c for c in self.contents
                        if not c.key.endswith('/')]

        res = self.client.list_objects_v2(
            Bucket=bucket,
            **kwargs
        )
        return Response(res)

    def put_object_function(self, bucket_name, prefix=None, raise_exc=False):
        bucket = self.bucket(bucket_name)

        def upload(file=None, key=None, source=None):
            key = key or os.path.basename(file)
            filekey = f"{prefix}/{key}" if prefix else key
            logger.info(f">> Upload file to S3: s3://{bucket_name}/{filekey}")
            try:
                obj = bucket.Object(filekey)

                if source:
                    res = obj.put(Body=source)
                elif file:
                    res = obj.upload_file(file)
                else:
                    logger.warning('Nothing to upload to s3')
                    res = None

            except Exception as e:
                logger.warning(f"Failed to upload file:"
                               f" s3://{bucket_name}/{filekey} : {e.args}")
                if raise_exc:
                    raise e

                res = None

            return res

        return upload
