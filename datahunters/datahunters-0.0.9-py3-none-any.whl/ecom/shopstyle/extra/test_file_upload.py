"""Test uploading image file to s3 and get url.
"""

import json

import boto3
from boto3.s3.transfer import S3Transfer

info = json.load(open("./aws_db_config.json", "r"))

credentials = {
    'aws_access_key_id': "AKIAILIZOLWO7H6IZVPA",
    'aws_secret_access_key': "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"
}

client = boto3.client('s3', 'us-east-1', **credentials)

# set content type.
# http://s3browser.com/features-content-mime-types-editor.aspx

# upload.
client.upload_file(
    './11199831_5723599_1000.jpg',
    'eyestyle.random',
    'test.jpg',
    extra_args={'ACL': 'public-read',
                'ContentType': 'image/jpeg'})

with open("./11199831_5723599_1000.jpg", "rb") as f:
  client.upload_fileobj(
      f,
      "eyestyle.random",
      "test.jpg",
      extra_args={'ACL': 'public-read',
                  'ContentType': 'image/jpeg'})

file_url = '%s/%s/%s' % (client.meta.endpoint_url, 'eyestyle.random',
                         'test.jpg')
print file_url

# download.
client.download_file("eyestyle.random", "test.jpg", "./test.jpg")
with open("./test.jpg", "wb") as f:
  client.download_fileobj("eyestyle.random", "test.jpg", f)
