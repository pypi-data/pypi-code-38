#/usr/bin/env python
"""
Functions to manage a template and wheter it should be stored in S3
"""
from datetime import datetime as dt
import hashlib
import boto3


def create_template_in_s3(bucket, file_name, template_body):
    """
    Args:
      bucket: name of the s3 bucket whereto upload the file
      the name of the file in S3
      template_body: the body of the template for CFN
    Returns:
      the URL to the file in S3 if successful, None if upload failed
    """
    date = dt.utcnow().isoformat()
    date_hash = hashlib.sha1(b'{date}').hexdigest()
    key = f'{file_name}'
    client = boto3.client('s3')
    client.put_object(
        Body=template_body,
        Key=key,
        Bucket=bucket
    )
    url_path = f'https://s3.amazonaws.com/{bucket}/{key}'
    return url_path
