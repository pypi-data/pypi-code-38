import logging
import fnmatch
import os
from urllib import parse

try:
    import boto3
except ImportError:
    boto3=None

logger = logging.getLogger("dativa.tools.aws.s3_lib")


class S3Location(str):
    """
    Class that parses out an S3 location from a passed string. Subclass of `str`
    so supports most string operations.

    Also contains properties .bucket, .key, .path, .prefix and method .join()

    :param s3_str: string representation of s3 location, accepts most common formats
        eg:
            - 's3://bucket/folder/file.txt'
            - 'bucket/folder'
            - 'http[s]://s3*.amazonaws.com/bucket-name/'
        also accepts None if using `bucket` and `key` keywords
    :param bucket: ignored if s3_str is not None. can specify only bucket for
        bucket='mybucket' - 's3://mybucket/' or in conjuction with `key`
    :param key: ignored if s3_str is not None. Bucket must be set.
        bucket='mybucket', key='path/to/file' - 's3://mybucket/path/to/file'
    :param ignore_double_slash: default False. If true allows s3 locations containing '//'
        these are valid s3 paths, but typically result from mistaken joins



    """

    def __new__(cls, s3_str=None, ignore_double_slash=False, bucket=None, key=None):

        if s3_str is None:
            s3_str = cls._from_kwargs(bucket, key)

        validated_string = cls._validate(s3_str, ignore_double_slash)

        instance = super(S3Location, cls).__new__(cls, validated_string)

        return instance

    def __init__(self, *args, **kwargs):

        super().__init__()

        self._bucket = self.split('/')[2]
        self._key = '/'.join(self.split('/')[3:])

    @staticmethod
    def _from_kwargs(bucket=None, key=None):

        if bucket is None:
            raise S3ClientError('could not resolve bucket')

        return "s3://{bucket}/{path}".format(bucket=bucket,
                                             path=key or '')

    @classmethod
    def _validate(self, s3_str, ignore_double_slash=False):

        result = parse.urlparse(s3_str)

        if result.port is not None:
            raise S3ClientError("S3 URLs cannot have a port")

        if result.password is not None:
            raise S3ClientError("S3 URLs cannot have a password (or username)")

        if result.username is not None:
            raise S3ClientError("S3 URLs cannot have a username")

        if result.scheme == "":
            if result.path.startswith("/"):
                raise S3ClientError("S3 URLS must have a prefix or not start with a /, "
                                    "current val: {}".format(s3_str))
            else:
                _bucket = result.path.split("/")[0]
                _key = "/".join(result.path.split("/")[1:])

        elif result.scheme == "s3":
            if result.hostname is None:
                raise S3ClientError("S3 URL is malformed, "
                                    "current val: {}".format(s3_str))
            _bucket = result.hostname
            _key = result.path[1:]
        elif result.scheme in ["http", "https"]:
            if result.hostname.startswith("s3") and result.hostname.endswith(".amazonaws.com"):
                _bucket = result.path.split("/")[1]
                _key = "/".join(result.path.split("/")[2:])
            else:
                raise S3ClientError("S3 HTTP URLS must be of the form http[s]://s3*.amazonaws.com/bucket-name/, "
                                    "current val: {}".format(s3_str))
        else:
            raise S3ClientError("S3 URLs must be either s3://, http://, or https://, "
                                "current val: {}".format(s3_str))

        s3_path = "s3://{bucket}/{path}".format(bucket=_bucket,
                                                path=_key or '')

        if not ignore_double_slash:
            if "//" in "{bucket}/{path}".format(bucket=_bucket,
                                                path=_key or ''):
                raise S3ClientError("S3 URLs cannot contains a // unless ignore_double_slash is set to True, "
                                    "current val: {}".format(s3_str))

        return s3_path

    @staticmethod
    def _coalesce_empty(s, n):
        if s == "":
            return n
        else:
            return s

    @property
    def file(self):
        return self._coalesce_empty(self._key.split("/")[-1], None)

    @property
    def prefix(self):

        return self._coalesce_empty("/".join(self._key.split("/")[0:-1]), None)

    @property
    def key(self):

        return self._coalesce_empty(self._key, None)

    @property
    def path(self):
        return self.key

    @property
    def bucket(self):
        return self._coalesce_empty(self._bucket, None)

    @property
    def s3_url(self):
        """deprecated - can use str, or in most cases simply the object itself"""
        return "s3://{bucket}/{path}".format(bucket=self.bucket,
                                             path=self.key or '')

    def join(self, *other, ignore_double_slash=False):
        """
        Join s3 location to string or list of strings similar to os.path.join
        eg.
            - s3.join('file')
            - s3.join('path', 'to', 'file')
        :param other: nargs to join,
        :param ignore_double_slash: default False. set true to allow '//' in the link, eg
            's3://bucket/folder//path/key'.
        :return: S3Location
        """

        to_join = '/'.join(other)

        if self.endswith('/'):
            joined = self.s3_url + to_join
        else:
            joined = self.s3_url + '/' + to_join

        return S3Location(joined, ignore_double_slash)

    def __repr__(self):
        return('S3Location(\'{}\')'.format(self))

    def __eq__(self, other):
        return self.s3_url == str(other)

    def __contains__(self, item):
        return self.__str__().__contains__(item)

    def __hash__(self):
        return hash(self.__str__())


class S3ClientError(Exception):
    """
    A generic class for reporting errors in the athena client
    """

    def __init__(self, reason):
        Exception.__init__(self, 'S3 Client failed: reason {}'.format(reason))
        self.reason = reason


class S3Client:
    """
    Class that provides easy access over boto s3 client
    """

    def __init__(self, boto3_client=None):
        if not boto3:
            raise ImportError("boto3 must be installed to run S3Client")

        self.s3_client = boto3_client if boto3_client else boto3.client(service_name='s3')

    def _files_within(self, directory_path, pattern):
        """
        Returns generator containing all the files in a directory
        """
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for file_name in fnmatch.filter(filenames, pattern):
                yield os.path.join(dirpath, file_name)

    def put_folder(self, source, bucket, destination="", file_format="*"):
        """
        Copies files from a directory on local system to s3
+        :param source: Folder on local filesystem that must be copied to s3
+        :param bucket: s3 bucket in which files have to be copied
+        :param destination: Location on s3 bucket to which files have to be copied
+        :param file_format: pattern for files to be transferred
+        :return: None
        """
        if os.path.isdir(source):
            file_list = list(self._files_within(source, file_format))
            for each_file in file_list:
                part_key = os.path.relpath(each_file, source)
                key = os.path.join(destination, part_key)
                self.s3_client.upload_file(each_file, bucket, key)
        else:
            raise S3ClientError("Source must be a valid directory path")

    def _generate_keys(self, bucket, prefix, suffix="", start_after=None):

        if start_after is None:
            s3_objects = self.s3_client.list_objects_v2(Bucket=bucket,
                                                        Prefix=prefix,
                                                        MaxKeys=1000)
        else:
            s3_objects = self.s3_client.list_objects_v2(Bucket=bucket,
                                                        Prefix=prefix,
                                                        MaxKeys=1000,
                                                        StartAfter=start_after)

        if 'Contents' in s3_objects:
            for key in s3_objects["Contents"]:
                if key['Key'].endswith(suffix):
                    yield key['Key']

            # get the next keys
            yield from self._generate_keys(bucket, prefix, suffix, s3_objects["Contents"][-1]['Key'])

    def delete_files(self, bucket, prefix, suffix=""):
        return self.delete("s3://{0}/{1}".format(bucket, prefix), suffix)

    def delete(self, path, suffix=""):
        loc = S3Location(path)
        keys = []
        for key in self._generate_keys(loc.bucket, loc.path, suffix):
            keys.append({'Key': key})
            if len(keys) == 1000:
                logger.info("Deleting {0} files in {1}".format(len(keys), loc.s3_url))
                self.s3_client.delete_objects(Bucket=loc.bucket,
                                              Delete={"Objects": keys})
                keys = []

        if len(keys) > 0:
            logger.info("Deleting {0} files in {1}".format(len(keys), loc.s3_url))
            self.s3_client.delete_objects(Bucket=loc.bucket,
                                          Delete={"Objects": keys})

    def list_files(self, bucket, prefix="", suffix=None, remove_prefix=False):
        return self.list("s3://{0}/{1}".format(bucket, prefix), suffix, remove_prefix)

    def list(self, path, suffix=None, remove_prefix=False):
        """
            Lists files with particular prefix/suffix stored on S3
            
            ## Parameters
            - bucket: S3 bucket in which files are stored
            - prefix: Prefix filter for files on S3
            - suffix: Suffix filter for files on S3
        """
        keys = []
        continue_flag = True
        continue_token = None

        loc = S3Location(path)

        while continue_flag:
            if continue_token:
                response = self.s3_client.list_objects_v2(Bucket=loc.bucket,
                                                          Prefix=loc.path if loc.path else "",
                                                          ContinuationToken=continue_token)
            else:
                response = self.s3_client.list_objects_v2(Bucket=loc.bucket,
                                                          Prefix=loc.path if loc.path else "")
            if response and 'Contents' in response and len(response['Contents']) > 0:
                # Get keys from response
                new_keys = map(lambda d: d['Key'], response['Contents'])
                # Filter keys by suffix
                if suffix:
                    new_keys = filter(lambda x: x.endswith(suffix), new_keys)
                # Remove prefix from keys
                if loc.path and remove_prefix:
                    new_keys = map(lambda x: x.replace(loc.path, ''), new_keys)
                # Save the keys
                keys.extend(new_keys)
                # Do we need to carry on?
                continue_flag = response['IsTruncated']
                if continue_flag and 'NextContinuationToken' in response:
                    continue_token = response['NextContinuationToken']
            else:
                continue_flag = False

        return keys
