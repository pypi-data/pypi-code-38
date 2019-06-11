import logging
import os
import tempfile
from unittest import TestCase

import six
from backports import tempfile as tf

from dli.client.exceptions import S3FileDoesNotExist, DownloadDestinationNotValid
from dli.client.s3 import Client, S3DatafileWrapper
from tests import localstack_helper
from tests.common import build_fake_s3fs

logger = logging.getLogger(__name__)


class S3ClientTestCase(TestCase):

    def setUp(self):
        self.target = Client("key", "secret", "token")
        self.target.s3fs = build_fake_s3fs("key", "sectet", "token")
        s3client = localstack_helper.get_s3_client()
        s3client.create_bucket(Bucket="bucket")

        def cleanup():
            files_to_delete = self.target.s3fs.walk("bucket")
            s3client.delete_objects(Bucket="bucket", Delete={"Objects": [{"Key": f.replace("bucket/", "", 1)} for f in files_to_delete]})
            s3client.delete_bucket(Bucket="bucket")

        self.addCleanup(cleanup)

    def test_download_file_validates_path_exists_in_s3(self):
        with self.assertRaises(S3FileDoesNotExist):
            with tf.TemporaryDirectory() as dest:
                self.target.download_files_from_s3_path("s3://unknown/file", dest)

    def test_download_file_validates_destination_is_a_directory(self):
        self.target.s3fs.put(__file__, "s3://bucket/file")
        with self.assertRaises(DownloadDestinationNotValid):
            with tempfile.NamedTemporaryFile() as cm:
                self.target.download_files_from_s3_path("s3://bucket/file", cm.name)

    def test_download_file_creates_destination_directory_if_it_doesnt_exist(self):
        self.target.s3fs.put(
            __file__,
            os.path.join("s3://bucket/location/", os.path.basename(__file__))
        )

        with tf.TemporaryDirectory() as dest:
            dest = os.path.join(dest, "dir1", "dir2")
            self.target.download_files_from_s3_path(
                "s3://bucket/location/test_s3_client.py",
                dest
            )

            self.assertTrue(os.path.exists(dest) and os.path.isdir(dest))
            self.assertTrue(os.path.exists(os.path.join(dest, "location", "test_s3_client.py")))

    def test_download_file_can_download_folders(self):
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/file1.txt")
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/subdir/file2.txt")
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/subdir/subdir/file3.txt")

        with tf.TemporaryDirectory() as dest:
            self.target.download_files_from_s3_path("s3://bucket/tdfcdf", dest)

            self.assertTrue(os.path.exists(dest))
            self.assertTrue(os.path.exists(os.path.join(dest, "tdfcdf", "file1.txt")))
            self.assertTrue(os.path.exists(os.path.join(dest, "tdfcdf", "subdir", "file2.txt")))
            self.assertTrue(os.path.exists(os.path.join(dest, "tdfcdf", "subdir", "subdir", "file3.txt")))

    def test_download_file_can_download_single_file(self):
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/file1.txt")

        with tf.TemporaryDirectory() as dest:
            self.target.download_files_from_s3_path("s3://bucket/tdfcdf/file1.txt", dest)

            self.assertTrue(os.path.exists(dest))
            self.assertTrue(os.path.exists(os.path.join(dest, "tdfcdf", "file1.txt")))


class S3DatafileWrapperTestCase(TestCase):

    def setUp(self):
        self.s3fs = build_fake_s3fs("key", "sectet", "token")

    def test_files_returns_files_in_datafile(self):
        files = [
            "s3://bucket/tfrfid/a",
            "s3://bucket/tfrfid/b",
            "s3://bucket/tfrfid/c",
        ]

        for f in files:
            self.s3fs.touch(f)

        datafile = {
            "files": [{"path": f} for f in files]
        }

        target = S3DatafileWrapper(datafile, self.s3fs)
        six.assertCountEqual(
            self,
            target.files,
            [f.replace("s3://", "") for f in files]
        )

    def test_files_will_recurse_directories(self):
        files = [
            "s3://bucket/tfwrd/a/aa",
            "s3://bucket/tfwrd/b/bb/bbb",
            "s3://bucket/tfwrd/c/cc/ccc/cccc1",
            "s3://bucket/tfwrd/c/cc/ccc/cccc2",
        ]

        # create sample files
        for f in files:
            self.s3fs.touch(f)

        datafile = {
            "files": [
                {'path': 's3://bucket/tfwrd/a'},
                {'path': 's3://bucket/tfwrd/b'},
                {'path': 's3://bucket/tfwrd/c'}
            ]
        }

        target = S3DatafileWrapper(datafile, self.s3fs)
        six.assertCountEqual(
            self,
            target.files,
            [f.replace("s3://", "") for f in files]
        )

    def test_only_files_in_datafile_are_displayed(self):
        files = [
            "s3://bucket/tofidad/a",
            "s3://bucket/tofidad/b",
            "s3://bucket/tofidad/c",
            "s3://bucket/tofidad/d"
        ]

        # create sample files
        for f in files:
            self.s3fs.touch(f)

        datafile = {
            "files": [{"path": f} for f in files[0:1]]
        }
        target = S3DatafileWrapper(datafile, self.s3fs)
        six.assertCountEqual(
            self,
            target.files,
            [f.replace("s3://", "") for f in files[0:1]]
        )

    def test_can_open_file(self):
        files = [
            "s3://bucket/tcof/a"
        ]
        # create sample files
        for f in files:
            self.s3fs.touch(f)
            with self.s3fs.open(f, mode="wb") as s3f:
                s3f.write(b"test 1")
                s3f.flush()

        datafile = {
            "files":  [{"path": f} for f in files]
        }

        target = S3DatafileWrapper(datafile, self.s3fs)

        with target.open_file("bucket/tcof/a") as s3file:
            self.assertIsNotNone(s3file)
            self.assertEquals(s3file.read(), b"test 1")

    def test_unknown_file_is_handled_gracefully(self):
        files = [
            "s3://bucket/tufihg/a"
        ]
        # create sample files
        for f in files:
            self.s3fs.touch(f)

        datafile = {
            "files": [{"path": f} for f in files]
        }

        target = S3DatafileWrapper(datafile, self.s3fs)

        with self.assertRaises(S3FileDoesNotExist):
            target.open_file("bucket/unknown/file")
