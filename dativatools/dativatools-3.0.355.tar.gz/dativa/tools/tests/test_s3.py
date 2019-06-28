import unittest
import logging
from dativa.tools.aws import S3Location, S3ClientError


logger = logging.getLogger("dativa.tools.aws.tests.s3")


# noinspection SqlNoDataSourceInspection
class S3Test(unittest.TestCase):

    def test_s3_url(self):
        loc = S3Location("s3://bucket/path/file")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/file", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertEqual("file", loc.file)
        self.assertEqual("s3://bucket/path/file", loc.s3_url)

    def test_s3_url_folder(self):
        loc = S3Location("s3://bucket/path/")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/path/", loc.s3_url)

    def test_has_port(self):
        with self.assertRaises(S3ClientError):
            loc = S3Location("s3://bucket:90/path/")

    def test_has_user(self):
        with self.assertRaises(S3ClientError):
            loc = S3Location("s3://user@bucket/path/")

    def test_has_password(self):
        with self.assertRaises(S3ClientError):
            loc = S3Location("s3://user:password@bucket/path/")

    def test_has_slash(self):
        with self.assertRaises(S3ClientError):
            loc = S3Location("/bucket")

    def test_bare_bucket(self):
        loc = S3Location("bucket")
        self.assertEqual("bucket", loc.bucket)
        self.assertIsNone(loc.path)
        self.assertIsNone(loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/", loc.s3_url)

    def test_bare_bucket_slash(self):
        loc = S3Location("bucket/")
        self.assertEqual("bucket", loc.bucket)
        self.assertIsNone(loc.path)
        self.assertIsNone(loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/", loc.s3_url)

    def test_bare_bucket_path(self):
        loc = S3Location("bucket/path")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path", loc.path)
        self.assertIsNone(loc.prefix)
        self.assertEqual("path", loc.file)
        self.assertEqual("s3://bucket/path", loc.s3_url)

    def test_http_bucket(self):
        loc = S3Location("http://s3.amazonaws.com/bucket/")
        self.assertEqual("bucket", loc.bucket)
        self.assertIsNone(loc.path)
        self.assertIsNone(loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/", loc.s3_url)

    def test_http_bucket_path(self):
        loc = S3Location("http://s3.amazonaws.com/bucket/path")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path", loc.path)
        self.assertIsNone(loc.prefix)
        self.assertEqual("path", loc.file)
        self.assertEqual("s3://bucket/path", loc.s3_url)

    def test_http_bucket_path_slash(self):
        loc = S3Location("http://s3-us-west-1.amazonaws.com/bucket/path/")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/path/", loc.s3_url)

    def test_http_bucket_path_file(self):
        loc = S3Location("http://s3-us-west-1.amazonaws.com/bucket/path/file")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/file", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertEqual("file", loc.file)
        self.assertEqual("s3://bucket/path/file", loc.s3_url)

    def test_https_bucket(self):
        loc = S3Location("https://s3-us-west-1.amazonaws.com/bucket/")
        self.assertEqual("bucket", loc.bucket)
        self.assertIsNone(loc.path)
        self.assertIsNone(loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/", loc.s3_url)

    def test_https_bucket_path(self):
        loc = S3Location("https://s3-us-west-1.amazonaws.com/bucket/path")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path", loc.path)
        self.assertIsNone(loc.prefix)
        self.assertEqual("path", loc.file)
        self.assertEqual("s3://bucket/path", loc.s3_url)

    def test_https_bucket_path_slash(self):
        loc = S3Location("https://s3-us-east-1.amazonaws.com/bucket/path/")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/path/", loc.s3_url)

    def test_https_bucket_path_file(self):
        loc = S3Location("https://s3.amazonaws.com/bucket/path/file")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/file", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertEqual("file", loc.file)
        self.assertEqual("s3://bucket/path/file", loc.s3_url)

    def test_https_invalid(self):
        with self.assertRaises(S3ClientError):
            S3Location("https://amazonaws.com/bucket/path/file")

    def test_https_invalid_2(self):
        with self.assertRaises(S3ClientError):
            S3Location("https://s3-amazonaws.com/bucket/path/file")

    def test_news(self):
        with self.assertRaises(S3ClientError):
            S3Location("news://s3-amazonaws.com/bucket/path/file")

    def test_mistyped_s3(self):
        with self.assertRaises(S3ClientError):
            S3Location("s3:/bucket/path/file")

    def test_double_slash(self):
        with self.assertRaises(S3ClientError):
            S3Location("s3://bucket/path//file")

    def test_double_slash_bucket(self):
        with self.assertRaises(S3ClientError):
            S3Location("bucket//path/file")

    def test_s3_str(self):
        s = "s3://bucket/path/file"
        self.assertEqual(str(S3Location(s)), s)

    def test_s3_repr(self):
        s = "s3://bucket/path/file"
        self.assertEqual(eval(repr(S3Location(s))), S3Location(s))

    def test_s3_eq(self):
        s = "bucket/path/file"

        self.assertTrue(S3Location(s) == "s3://bucket/path/file")

    def test_s3_in(self):
        s = "bucket/path/file"

        self.assertTrue('/bucket/' in S3Location(s))


    def test_s3_startswith(self):
        s = "bucket/path/file"

        self.assertTrue(S3Location(s).startswith('s3://'))

    def test_join_str(self):

        self.assertEqual(S3Location('bucket/key/file.txt'),
                         S3Location('bucket/key').join('file.txt'))

    def test_join_many(self):

        self.assertEqual(S3Location('bucket/key/file.txt'),
                         S3Location('bucket').join('key', 'file.txt'))

    def test_no_key(self):

        self.assertEqual(S3Location('s3://bucket').key,
                         None)

    def test_keyword_constructor(self):

        self.assertEqual(S3Location('s3://bucket/key'),
                         S3Location(bucket='bucket', key='key'))

    def test_keyword_constructor_no_key(self):
        self.assertEqual(S3Location('s3://bucket/'),
                         S3Location(bucket='bucket'))

    def test_keyword_constructor_no_bucket_error(self):

        with self.assertRaises(S3ClientError):
            S3Location(key='key')

    def test_what_error(self):
        with self.assertRaises(S3ClientError):
            S3Location()

    def test_construct_from_self(self):

        self.assertEqual(S3Location('s3://bucket/key'),
                         S3Location(S3Location('s3://bucket/key')))

