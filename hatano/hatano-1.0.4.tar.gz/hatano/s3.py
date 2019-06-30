from hatano.util import region

import boto3
import hashlib
import json
import os

def make_cf_policy(bucket_name, access_id):
    access_id = os.path.basename(access_id)
    arn = f"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity {access_id}"


    policy = {
    "Version": "2008-10-17",
    "Id": "PolicyForCloudFrontPrivateContent",
    "Statement": [
        {
            "Sid": "1",
            "Effect": "Allow",
            "Principal": {
                "AWS": f"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity {access_id}"
            },
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }
        ]
    }
    return policy

cors_config = {
        'CORSRules': [
            {
                'AllowedHeaders': [
                    '*',
                ],
                'AllowedMethods': [
                    'GET',
                ],
                'AllowedOrigins': [
                    '*',
                ],
                'MaxAgeSeconds': 1800
            },
        ]
    }


class S3:
    def __init__(self, path, proj, stage):
        self.path = path
        self.proj = proj
        self.stage = stage
        self.s3 = boto3.client('s3')

    def upload_all(self):
        for dname,_,fnames in os.walk(self.path):
            for fname in fnames:
                fpath = os.path.join(dname, fname)
                self.upload(fpath)

    def upload(self, fname):
        head = f"{self.path}{os.path.sep}"
        s3name = fname
        if s3name.startswith(head):
            s3name = s3name[len(head):]

        return self.s3.upload_file(fname, self.name(), s3name)

    def name(self):
        msg = '|'.join([self.proj, self.stage]).encode()
        suffix = hashlib.sha256(msg).hexdigest()[:8]
        bucket_name = f"{self.proj}-{self.stage}-{suffix}"
        return bucket_name

    def create(self):
        name = self.name()
        return self.s3.create_bucket(
                Bucket=name,
                CreateBucketConfiguration={
                    'LocationConstraint': region})

    def delete(self):
        name = self.name()
        return self.s3.delete_bucket(Bucket=name)

    def empty(self):
        res = boto3.resource('s3')
        bucket = res.Bucket(self.name())
        bucket.objects.all().delete()

    def put_policy(self, access_id):
        self.s3.put_bucket_policy(
                Bucket=self.name(),
                Policy=json.dumps(make_cf_policy(self.name(), access_id)))

    def put_cors(self):
        self.s3.put_bucket_cors(
                Bucket=self.name(),
                CORSConfiguration=cors_config)
                

