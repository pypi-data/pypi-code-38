import boto3
import botocore
import os
import shutil

import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

class S3DataHelper():

    def __init__(self, config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.connect()

    def connect(self):
        self.s3 = boto3.resource(
            's3',
            region_name=self.config['region'])
        self.s3bucket = self.config['s3bucket']

    def list_object(self, prefix):
        response = self.s3.meta.client.list_objects_v2(
            Bucket=self.s3bucket,
            Prefix=prefix)
        if 'Contents' in response:
            return response['Contents']
        else:
            self.logger.warn('No contents in s3(Bucket=%s, prefix=%s)' %(self.s3bucket, prefix))
            return []

    def get_keys(self, prefix):
        """Get a list of all keys in an S3 bucket."""
        keys = []

        kwargs = {'Bucket': self.s3bucket, 'Prefix': prefix}
        while True:
            resp = self.s3.meta.client.list_objects_v2(**kwargs)
            if 'Contents' not in resp:
                break
            for obj in resp['Contents']:
                keys.append(obj['Key'])

            try:
                kwargs['ContinuationToken'] = resp['NextContinuationToken']
            except KeyError:
                break
        
        if len(keys)==0:
            self.logger.warn('No contents in s3(Bucket=%s, prefix=%s)' %(self.s3bucket, prefix))

        return keys

    def upload_file(self, s3path, local_file):
        self.logger.info('put %s to s3 (bucket=%s, key=%s)' % (local_file, self.s3bucket, s3path))

        self.s3.meta.client.upload_file(
            local_file,
            self.s3bucket,
            s3path)

    def upload_folder(self, s3folder, local_dir):
        '''
        upload a local folder to S3 (with success file)
        '''
        self.logger.info('put %s to s3 (bucket=%s, key=%s)' % (local_dir, self.s3bucket, s3folder))

        files = os.listdir(local_dir)
        err_cnt = 0
        for file in files:
            path = '%s/%s' % (local_dir, file)
            s3_path = '%s/%s' % (s3folder, file)
            try: 
                self.s3.meta.client.upload_file(
                    path,
                    self.s3bucket,
                    s3_path)
                self.logger.info('put %s to s3 (bucket=%s, key=%s)' % (path, self.s3bucket, s3_path))
            except Exception as e:
                self.logger.warning("failed to upload file %s to s3://%s/%s" % (path, self.s3bucket, s3_path))
                self.logger.warning(e)
                err_cnt += 1

        if err_cnt==0:
            self.s3.meta.client.put_object(
                    Bucket=self.s3bucket,
                    Key='%s/%s' % (s3folder, '_SUCCESS'))

    def download_file(self, s3path, local_file):
        self.logger.info('get %s from s3 (bucket=%s, key=%s)' % (local_file, self.s3bucket, s3path))
        try:
            self.s3.Bucket(self.s3bucket).download_file(s3path, local_file)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                self.logger.warn("The object in s3 (bucket=%s, key=%s) does not exist." % (self.s3bucket, s3path))
            else:
                raise

    def download_folder(self, s3folder, local_dir):
        self.logger.info('get %s from s3 (bucket=%s, key=%s)' % (local_dir, self.s3bucket, s3folder))

        objs = self.list_object(s3folder)
        if len(objs)==0:
            return

        self.mkdir(local_dir)
        for obj in objs:
            s3path = obj['Key']
            local_file = '%s%s'% (local_dir, s3path[len(s3folder):])
            self.download_file(s3path, local_file)

    def mkdir(self, root_dir):
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)

    def rmdir(self, root_dir):
        '''
        Caution!
        It's dangerous like 'rm -rf'
        '''
        if root_dir[0]!='/':
            shutil.rmtree(root_dir)


    

    

