import pathlib
import sys
from logging import StreamHandler

import boto3
import cloudpickle
import s3fs
from loguru import logger
from s3fs.mapping import S3Map

"""
    This is a storage adapter that will be used to place any kind of serialized data inside of any cloud system as well as call that very same data

    storage = Storage(location="s3", key="", secret="", bucket="s3")
    storage = Storage(location="azure", key="", secret="")
    storage = Storage(location="local")


    storage.add(...)
    file = storage.get(...)
"""

logger.add(StreamHandler(sys.stderr), format="{message}")
logger.add("file_test.log")

__AVAILABLE_PROVIDERS__ = ['s3', 'azure', 'google', 'gcloud', 'local']

class SpaceStorage(object):
    def __init__(self, provider="s3", key=None, secret=None, token=None, folder_bucket_name="checkpoint", local_folder="/tmp"):
        
        if provider not in __AVAILABLE_PROVIDERS__:
            raise AttributeError(f"Provider not accepted. Please use the following: {__AVAILABLE_PROVIDERS__}")
        

        self.fs = None
        self.provider = provider
        self.bucket = folder_bucket_name
        self.local_folder = local_folder

        # Start off seeing if we're passes keys. If not, we will just get the local interface to work for us
        client = None
        if provider != "local":
            if self.determine_use_key(key, secret, token):
                valid_keys = self.check_provider_keys(provider, key, secret)
                if valid_keys == False:
                    raise ValueError("Your keys aren't valid")
                self.get_provider(provider, True, key, secret, token)
            self.get_provider(provider)
        # elif provider == "local":
        #     """ Create the storage folder """
        #     pathlib.Path(f"{local_folder}/{folder_bucket_name}")
        
        self.create_container_or_bucket()


    def determine_use_key(self, provider, key, secret, token=None):
        """ Determine if we're using a direct key """
        if (key is None or secret is None) and token is None:
            return False
        return True

    def get_provider(self, provider, is_hard=False, key=None, secret=None, token=None):
        """ Get the provider here. Use to automatically handle various providers"""
        if provider == "s3":
            if is_hard:
                self.fs = s3fs.S3FileSystem(key=key, secret=secret, token=token)
            else:
                self.fs = s3fs.S3FileSystem()


    def check_provider_keys(self, provider, key, secret, token=None):
        """ Checks the keys for the provider """
        if provider == "local":
            print("It's local storage. Automatic true.")
            return True
        elif provider == "s3":
            return self.check_aws(key, secret)
        elif provider == "azure":
            return self.check_azure(key, secret)
        elif provider == "google":
            return self.check_google(key, secret)

    def check_aws(self, key, secret, token):
        try:
            if (key is None or secret is None):
                client = boto3.client(
                    's3',
                    aws_session_token=token,
                )
            else:
                boto3.client(
                    's3',
                    aws_access_key_id=key,
                    aws_secret_access_key=secret
                )
        except Exception:
            return False
        return True
    
    def check_azure(self, key, secret):
        return True
    
    def check_google(self, key, secret):
        return True

    # ----------------------------------------------------------------
    # ----------------------- Bucket Management ----------------------
    # ----------------------------------------------------------------
    
    def create_container_or_bucket(self):
        """ Creates bucket or container if it doesn't exist within the given provider """
        if self.provider == "local":
            pathlib.Path(f"{self.local_folder}/{self.bucket}").mkdir(parents=True, exist_ok=True)
        if self.provider == "s3":
            try:
                mapping = S3Map(self.bucket, s3=self.fs, check=True)
            except Exception as e:
                if type(e).__name__ == "NoSuchBucket":
                    logger.info("No bucket available. Creating")
                    self.fs.mkdir(self.bucket)

    
    def add(self, obj, filename):
        bff = cloudpickle.dumps(obj)
        location = ""
        if self.provider == "local":
            location = f"{self.local_folder}/{self.bucket}/{filename}"
            p = pathlib.Path(location)
            p.write_bytes(bff)
        if self.provider == "s3":
            location = f"{self.bucket}/{filename}"
            with self.fs.open(location, mode='wb') as f:
                f.write(bff)
        
        # Return the location of the file (loc)
        return {
            "loc": location,
            "provider": self.provider,
        }
        
    def get(self, filename):
        _r = {
            "provider": self.provider
        }
        if self.provider == "local":
            location = f"{self.local_folder}/{self.bucket}/{filename}"
            _r["loc"] = location
            p = pathlib.Path(location)
            if p.exists():
                cerealized = p.read_bytes()
                _r["exist"] = True
                _r["file"] = cloudpickle.loads(cerealized)
            else:
                _r["exist"] = False
                _r["file"] = None
        if self.provider == "s3":
            location = f"{self.bucket}/{filename}"
            _r["loc"] = location
            if self.fs.exists(location):
                with self.fs.open(location, mode='rb') as f:
                    cerealized = f.read()
                    _r["exist"] = True
                    _r["file"] = cloudpickle.loads(cerealized)
            else:
                _r["exist"] = False
                _r["file"] = None
        return _r
