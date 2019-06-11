import s3fs
import os
import logging
import six
import glob2 as glob

from six.moves.urllib.parse import urlparse

from dli.client.exceptions import (
    is_boto_client_access_denied_error,
    DownloadDestinationNotValid,
    InsufficientPrivilegesException,
    S3FileDoesNotExist,
)

from dli.client import utils


logger = logging.getLogger(__name__)


class Client:
    """
    A wrapper client providing util methods for s3fs
    """
    def __init__(self, key, secret, token):
        self.s3fs = build_s3fs(key, secret, token)

    def download_files_from_s3_path(self, s3_path, destination):
        """
        Helper function to download a file as a stream from S3
        :param s3_path, required, example: s3://bucket_name/prefix_part1/prefix_part2/file_name.txt
        :param destination, required, must be a directory, if doesn't exist, will be created
        """

        if not self.s3fs.exists(s3_path):
            logger.warning("Attempted to download `%s` from S3 but the path does not exist", s3_path)
            raise S3FileDoesNotExist(s3_path)

        if not os.path.exists(destination):
            utils.makedirs(destination, exist_ok=True)

        if not os.path.isdir(destination):
            raise DownloadDestinationNotValid(
                "Expected destination=`%s` to be a directory" % destination
            )

        # s3_path can point to a directory or a file,
        files_in_s3_path = self.s3fs.walk(s3_path) or [s3_path]
        self._download_files(destination, files_in_s3_path)

    def _download_files(self, destination, files_in_path):
        for path in files_in_path:
            # path should be a s3 path (containing bucket) without the s3:// schema
            output_directory = self._prepare_output_directory(destination, path)

            self.s3fs.get(
                path,
                output_directory
            )

    def _prepare_output_directory(self, destination, path):
        output_directory = utils.path_for(
            destination,
            self._remove_s3_schema_and_bucket(path)
        )

        if not output_directory.parent.exists():
            output_directory.parent.mkdir(parents=True)

        return str(output_directory)

    def _remove_s3_schema_and_bucket(self, path):
        return path.replace("s3://", "").split("/", 1)[1]

    def upload_files_to_s3(self, files, s3_location, token_refresher=None, num_retries=3):
        """
        Upload multiple files to a specified s3 location. The basename of the
        `files` will be preserved.

        :param List files: An list of filepaths
        :param str s3_location: Path to destination directory in S3, file will be
                 stored under <s3_location><filename>
        :param token_refresher: Optional Function to refresh S3 token
        :param int num_retries: Optional Number of retries in case of upload failure.
        :returns: List of path to the files in S3
        :rtype: List[str]
        """
        def upload(file, s3_location):
            file_path = file['file']
            s3_suffix = file['s3_suffix']
            target = os.path.join(s3_location, s3_suffix)

            logger.info("Uploading %s to %s", file_path, target)

            try:
                self.s3fs.put(file_path, target)
            except Exception as e:
                if is_boto_client_access_denied_error(e):
                    raise InsufficientPrivilegesException()
                raise e

            logger.info(".. %s uploaded successfully.", file_path)

            return {
                "path": "s3://%s" % target,
                "size": os.path.getsize(file_path)
            }

        def upload_or_retry(file, s3_location, on_error, retries):
            try:
                return upload(file, s3_location)
            except InsufficientPrivilegesException as e:
                raise e
            except Exception as e:
                logger.exception("Failed to upload file to S3: %s", e)
                if retries > 0:
                    on_error()
                    return upload_or_retry(file, s3_location, on_error, retries - 1)
                else:
                    raise e

        def on_error():
            if token_refresher:
                s3_access_keys = token_refresher()
                self.s3fs = build_s3fs(
                    key=s3_access_keys.access_key_id,
                    secret=s3_access_keys.secret_access_key,
                    token=s3_access_keys.session_token
                )

        files_to_upload = self._files_to_upload_flattened(files)
        result = []
        for file in files_to_upload:
            uploaded = upload_or_retry(
                file,
                s3_location,
                on_error,
                num_retries
            )

            result.append(uploaded)

        return result

    @staticmethod
    def _files_to_upload_flattened(files):
        files_to_upload = []

        for file in files:
            if not os.path.exists(file):
                raise Exception('File / directory specified (%s) for upload does not exist.' % file)

            if os.path.isfile(file):
                logger.info("detected file: %s", file)
                files_to_upload.append({'file': file, 's3_suffix': os.path.basename(file)})
            elif os.path.isdir(file):
                logger.info("detected directory: %s", file)
                all_contents = glob.glob(os.path.join(file, "**/*"), recursive=True)
                fs = [f for f in all_contents if os.path.isfile(f)]

                for f in fs:
                    files_to_upload.append({'file': f, 's3_suffix': os.path.relpath(f, file)})

        return files_to_upload


def build_s3fs(key, secret, token):
    """
    Factory function to create an s3fs client.
    Extracted as a function so that it can
    be easily mocked / patched.
    """
    return s3fs.S3FileSystem(key=key, secret=secret, token=token)


class S3DatafileWrapper:
    def __init__(self, datafile, s3fs):
        # we want to override the files property
        # it isn't really needed for py3 but it is in py2
        self.__dict__ = {
            k: v for k,v in six.iteritems(datafile) if k != "files"
        }
        self._datafile = datafile
        self._s3 = s3fs

    def __getitem__(self, path):
        """
        :param str path: The path of the file to retrieve from s3.
        :returns: A S3File instance
        """
        return self.open_file(path)

    def open_file(self, path):
        """
        Helper method to load an specific file inside a datafile
        without having to download all of it.

        :param str path: The path of the file to retrieve from s3.
        :returns: A S3File instance that can be used as a normal python file
        """
        if not self._s3.exists(path):
            raise S3FileDoesNotExist(path)

        return self._s3.open(path, mode='rb')

    def __repr__(self):
        return str(dict(self._datafile))

    @property
    def files(self):
        """
        Lists all S3 files in this datafile, recursing on folders (if any)
        """
        result = []
        files = [file["path"] for file in self._datafile["files"]]

        for file in files:
            children = self._s3.walk(file)

            # are we downloading an specific file?
            if not children:
                result.append(file.replace("s3://", ""))
                continue

            result.extend(children)

        return result
