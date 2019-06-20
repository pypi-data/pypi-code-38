import unittest

from flywheel_common.storage import util

class StorageUtilTestCases(unittest.TestCase):

    def test_parse_storage_url(self):

        scheme, bucket_name, path, query = util.parse_storage_url('gc://bucket')
        self.assertEqual(scheme, 'gc')
        self.assertEqual(bucket_name, 'bucket')
        self.assertEqual(path, '')
        self.assertEqual(query, {})

        scheme, bucket_name, path, query = util.parse_storage_url('s3://another_bucket/path?key=1')
        self.assertEqual(scheme, 's3')
        self.assertEqual(bucket_name, 'another_bucket')
        self.assertEqual(path, '/path')
        self.assertEqual(query, {'key': '1'})

