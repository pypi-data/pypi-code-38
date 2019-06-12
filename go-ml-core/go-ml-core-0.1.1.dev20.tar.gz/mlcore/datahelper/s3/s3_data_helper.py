import boto3
import botocore
import os
import shutil
import random

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
        ###################################################
        '''
        return s3 resource
        '''
        def get_s3_resource(config):    
            if 'role-arn' in config and config['role-arn']!='':
                if 'aws-access-key-id' in config and 'aws-secret-access-key' in config:
                    sts_client = boto3.client(
                        'sts',
                        aws_access_key_id=config['aws-access-key-id'],
                        aws_secret_access_key=config['aws-secret-access-key'],
                        region_name=config['region'])
                else:
                    sts_client = boto3.client('sts')

                session_name = '%s-%s'%(config['role-session-name'], str(random.randint(1,100)))
                #self.logger.info('session_name = %s' % session_name)
                assumed_role_object = sts_client.assume_role(
				    RoleArn=config['role-arn'],
				    RoleSessionName=session_name)
                credentials = assumed_role_object['Credentials']
            
                s3 = boto3.resource(
				    's3',
				    aws_access_key_id=credentials['AccessKeyId'],
				    aws_secret_access_key=credentials['SecretAccessKey'],
				    aws_session_token=credentials['SessionToken'],
                    region_name=config['region'])
            else:
                if 'aws-access-key-id' in config and 'aws-secret-access-key' in config:
                    s3 = boto3.resource(
                        's3',
                        aws_access_key_id=config['aws-access-key-id'],
                        aws_secret_access_key=config['aws-secret-access-key'],
                        region_name=config['region'])
                else:
                    s3 = boto3.resource(
                        's3',
                        region_name=config['region'])

            if 's3baseprefix' in config:
                return {
                    's3': s3,
                    's3bucket': config['s3bucket'],
                    's3baseprefix': config['s3baseprefix']
                }
            else:
                return {
                    's3': s3,
                    's3bucket': config['s3bucket'],
                    's3baseprefix': 'ml/'
                }
        ###################################################
        
        # s3 read workspace
        if 'read' in self.config:
            self.s3read = get_s3_resource(self.config['read'])
        else:
            self.s3read = None
        # s3 write workspace
        if 'write' in self.config:
            self.s3write = get_s3_resource(self.config['write'])
        else:
            self.s3write = self.s3read

    def is_object_exist(self, key, is_write=False):
        '''
        check if an object in exist (True) or not (False)
        '''
        self.connect()
        s3 = self.s3read
        if is_write==True:
            s3 = self.s3write

        response = s3['s3'].meta.client.list_objects_v2(
            Bucket=s3['s3bucket'],
            Prefix=key,
        )
        for obj in response.get('Contents', []):
            if obj['Key'] == key:
                return True
        return False

    def list_object(self, prefix, is_write=False):
        self.connect()
        s3 = self.s3read
        if is_write==True:
            s3 = self.s3write

        response = s3['s3'].meta.client.list_objects_v2(
            Bucket=s3['s3bucket'],
            Prefix=prefix)
        if 'Contents' in response:
            return response['Contents']
        else:
            self.logger.warn('No contents in s3(Bucket=%s, prefix=%s)' % (s3['s3bucket'], prefix))
            return []

    def get_keys(self, prefix, is_write=False):
        """Get a list of all keys in an S3 bucket."""

        self.connect()
        s3 = self.s3read
        if is_write==True:
            s3 = self.s3write

        keys = []

        kwargs = {'Bucket': s3['s3bucket'], 'Prefix': prefix}
        while True:
            resp = s3['s3'].meta.client.list_objects_v2(**kwargs)
            if 'Contents' not in resp:
                break
            for obj in resp['Contents']:
                keys.append(obj['Key'])

            try:
                kwargs['ContinuationToken'] = resp['NextContinuationToken']
            except KeyError:
                break
        
        if len(keys)==0:
            self.logger.warn('No contents in s3(Bucket=%s, prefix=%s)' % (s3['s3bucket'], prefix))

        return keys

    def get_folder_prefixes(self, prefix, is_write=False):
        self.connect()
        s3 = self.s3read
        if is_write==True:
            s3 = self.s3write

        keys = []
        kwargs = {'Bucket': s3['s3bucket'], 'Prefix': prefix, 'Delimiter': '/'}

        while True:
            resp = s3['s3'].meta.client.list_objects_v2(**kwargs)
            if 'CommonPrefixes' not in resp:
                break

            for obj in resp['CommonPrefixes']:
                keys.append(obj['Prefix'])

            try:
                kwargs['ContinuationToken'] = resp['NextContinuationToken']
            except KeyError:
                break
        
        if len(keys)==0:
            self.logger.warn('No folders in s3(Bucket=%s, prefix=%s)' % (s3['s3bucket'], prefix))

        return keys

    def delete_files(self, list_s3path, max_keys=1000):
        '''
        This operation enables you to delete multiple objects from a bucket using a single HTTP request. 
        You may specify up to 1000 keys.
        '''
        self.connect()

        self.logger.info('delete files in s3 (bucket=%s, key=%s)' % (self.s3write['s3bucket'], list_s3path))

        n = len(list_s3path)
        cur = 0
        while cur < n:
            objs = [ {'Key':s3path} for s3path in list_s3path[cur:cur+max_keys]]
            self.s3write['s3'].meta.client.delete_objects(
                Bucket=self.s3write['s3bucket'],
                Delete={
                    'Objects': objs
                }
            )
            cur += max_keys
        # self.s3write['s3'].meta.client.delete_object(
        #     Bucket=self.s3write['s3bucket'],
        #     Key=list_s3path
        # )

    def delete_folder(self, s3folder):
        '''
        delete a s3 folder
        '''
        if s3folder[-1] != '/':
            self.logger.warn('not a valid s3folder %s' % s3folder)
            return

        self.connect()

        self.logger.info('delete folder in s3 (bucket=%s, key=%s)' % (self.s3write['s3bucket'], s3folder))

        objs = self.list_object(s3folder, is_write=True)
        if len(objs)==0:
            return

        list_s3path = []
        for obj in objs:
            list_s3path.append(obj['Key'])
            #self.delete_file(s3path)
        self.delete_files(list_s3path)

        

    def upload_file(self, s3path, local_file):
        self.connect()
        self.logger.info('put %s to s3 (bucket=%s, key=%s)' % (local_file, self.s3write['s3bucket'], s3path))

        self.s3write['s3'].meta.client.upload_file(
            local_file,
            self.s3write['s3bucket'],
            s3path)

    def upload_folder(self, s3folder, local_dir):
        '''
        upload a local folder to S3 (with success file)
        '''

        if s3folder[-1] != '/':
            self.logger.warn('not a valid s3folder %s' % s3folder)
            return
        if local_dir[-1] != '/':
            self.logger.warn('not a valid local_dir %s' % local_dir)
            return

        self.connect()
        self.logger.info('put %s to s3 (bucket=%s, key=%s)' % (local_dir, self.s3write['s3bucket'], s3folder))

        files = os.listdir(local_dir)
        err_cnt = 0
        for file in files:
            local_file = '%s%s' % (local_dir, file)
            s3_path = '%s%s' % (s3folder, file)
            try: 
                self.upload_file(s3_path, local_file)
            except Exception as e:
                self.logger.warning("failed to upload file %s to s3://%s/%s" % (path, self.s3write['s3bucket'], s3_path))
                self.logger.warning(e)
                err_cnt += 1

        if err_cnt==0:
            success_file_path = '%s%s' % (s3folder, '_SUCCESS')
            self.logger.info("put _SUCCESS to s3 (bucket=%s, key=%s)" % (self.s3write['s3bucket'], success_file_path))
            self.s3write['s3'].meta.client.put_object(
                    Bucket=self.s3write['s3bucket'],
                    Key=success_file_path)

    def download_file(self, s3path, local_file):
        self.connect()
        self.logger.info('get %s from s3 (bucket=%s, key=%s)' % (local_file, self.s3read['s3bucket'], s3path))
        try:
            self.mkdir("/".join(local_file.split('/')[:-1]) + "/")
            self.s3read['s3'].Bucket(self.s3read['s3bucket']).download_file(s3path, local_file)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                self.logger.warn("The object in s3 (bucket=%s, key=%s) does not exist." % (self.s3read['s3bucket'], s3path))
            else:
                raise

    def download_folder(self, s3folder, local_dir):
        '''
        dowload a s3 folder to a local folder 
        '''

        if s3folder[-1] != '/':
            self.logger.warn('not a valid s3folder %s' % s3folder)
            return
        if local_dir[-1] != '/':
            self.logger.warn('not a valid local_dir %s' % local_dir)
            return

        self.connect()
        self.logger.info('get %s from s3 (bucket=%s, key=%s)' % (local_dir, self.s3read['s3bucket'], s3folder))

        objs = self.list_object(s3folder)
        if len(objs)==0:
            return

        self.mkdir(local_dir)
        for obj in objs:
            s3path = obj['Key']
            local_file = '%s%s'% (local_dir, s3path[len(s3folder):])
            #self.logger.info('local_dir=%s, s3path=%s, s3path[len(s3folder):]=%s' % (local_dir, s3path, s3path[len(s3folder):]))
            self.download_file(s3path, local_file)

    def mkdir(self, root_dir):
        try :
            if not os.path.exists(root_dir):
                self.logger.info('create local dir: %s' % root_dir)
                os.makedirs(root_dir)
        except e:
            raise

    def rmdir(self, root_dir):
        '''
        Caution!
        It's dangerous like 'rm -rf'
        '''
        if root_dir[0]!='/':
            shutil.rmtree(root_dir)


    

    

