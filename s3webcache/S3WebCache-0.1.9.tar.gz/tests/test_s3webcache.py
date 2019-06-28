from unittest import TestCase
import os
import json

from s3webcache import S3WebCache

class TestCache(TestCase):
    def setUp(self):
        with open('config.creds.json') as f:
            self.creds = json.load(f)
        print(self.creds)
        self.valid_s3wc = S3WebCache(
            bucket_name=self.creds['BUCKET'],
            aws_access_key_id=self.creds['AWS_ACCESS_KEY_ID'],
            aws_secret_key=self.creds['AWS_SECRET_ACCESS_KEY'],
            aws_default_region=self.creds['AWS_DEFAULT_REGION'])

    def test_no_creds(self):
        print(self.creds)
        with self.assertRaises(Exception):
            s3wc = S3WebCache(bucket_name='', aws_access_key_id=None)

    def test_with_creds(self):
        self.assertTrue(self.valid_s3wc.bucket, self.creds['BUCKET'])
    
    def test_get_success(self):
        request = self.valid_s3wc.get(self.creds['URL'])
        self.assertTrue(request.success)
    
    def test_get_message(self):
        request = self.valid_s3wc.get(self.creds['URL'])
        self.assertIsInstance(request.message, str)

    

