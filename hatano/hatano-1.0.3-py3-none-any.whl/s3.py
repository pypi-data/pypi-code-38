from hatano.util import region

import boto3
import hashlib

import os


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

