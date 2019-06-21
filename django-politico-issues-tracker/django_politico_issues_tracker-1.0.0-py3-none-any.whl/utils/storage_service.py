from storages.backends.s3boto3 import S3Boto3Storage
from issuestracker.conf import settings


class StorageService(S3Boto3Storage):
    bucket_name = settings.AWS_S3_BUCKET
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    file_overwrite = False
    querystring_auth = False
    object_parameters = {"CacheControl": "max-age=86400", "ACL": "public-read"}
    custom_domain = settings.CLOUDFRONT_ALTERNATE_DOMAIN
    location = settings.S3_UPLOAD_ROOT
