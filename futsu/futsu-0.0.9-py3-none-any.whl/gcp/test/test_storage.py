from unittest import TestCase
import futsu.gcp.storage as fstorage
import futsu.fs as ffs
import tempfile
import os
from google.cloud import storage as gcstorage
import time

class TestStorage(TestCase):

    def test_is_gs_bucket_path(self):
        self.assertTrue(fstorage.is_gs_bucket_path('gs://bucket'))
        self.assertTrue(fstorage.is_gs_bucket_path('gs://bucket/'))

        self.assertFalse(fstorage.is_gs_bucket_path('gs://bucket//'))
        self.assertFalse(fstorage.is_gs_bucket_path('gs://bucket/asdf'))
        self.assertFalse(fstorage.is_gs_bucket_path('gs://bucket/asdf/'))
        self.assertFalse(fstorage.is_gs_bucket_path('gs://bucket/asdf/asdf'))

        self.assertFalse(fstorage.is_gs_bucket_path('s://bucket'))
        self.assertFalse(fstorage.is_gs_bucket_path('g://bucket'))
        self.assertFalse(fstorage.is_gs_bucket_path('gs//bucket'))
        self.assertFalse(fstorage.is_gs_bucket_path('gs:/bucket'))
        self.assertFalse(fstorage.is_gs_bucket_path('gs://'))
        self.assertFalse(fstorage.is_gs_bucket_path('gs:///'))
        self.assertFalse(fstorage.is_gs_bucket_path('gs:///asdf'))

    def test_is_gs_file_path(self):
        self.assertFalse(fstorage.is_gs_file_path('gs://bucket'))
        self.assertFalse(fstorage.is_gs_file_path('gs://bucket/'))

        self.assertTrue(fstorage.is_gs_file_path('gs://bucket//'))
        self.assertTrue(fstorage.is_gs_file_path('gs://bucket/asdf'))
        self.assertTrue(fstorage.is_gs_file_path('gs://bucket/asdf/'))
        self.assertTrue(fstorage.is_gs_file_path('gs://bucket/asdf/asdf'))

        self.assertFalse(fstorage.is_gs_file_path('s://bucket'))
        self.assertFalse(fstorage.is_gs_file_path('g://bucket'))
        self.assertFalse(fstorage.is_gs_file_path('gs//bucket'))
        self.assertFalse(fstorage.is_gs_file_path('gs:/bucket'))
        self.assertFalse(fstorage.is_gs_file_path('gs://'))
        self.assertFalse(fstorage.is_gs_file_path('gs:///'))
        self.assertFalse(fstorage.is_gs_file_path('gs:///asdf'))

    def test_parse_bucket_path(self):
        self.assertEqual(fstorage.prase_bucket_path('gs://asdf'),'asdf')
        self.assertRaises(ValueError,fstorage.prase_bucket_path,'asdf')

    def test_parse_file_path(self):
        self.assertEqual(fstorage.prase_file_path('gs://asdf/qwer'),('asdf','qwer'))
        self.assertEqual(fstorage.prase_file_path('gs://asdf/qwer/'),('asdf','qwer/'))
        self.assertRaises(ValueError,fstorage.prase_file_path,'asdf')

    def test_gcp_string(self):
        timestamp = int(time.time())
        tmp_gs_path  = 'gs://futsu-test/test-LAVVKOIHAT-{0}'.format(timestamp)

        client = gcstorage.client.Client()
        fstorage.set_string(tmp_gs_path,'JLPUSLMIHV',client)
        s = fstorage.get_string(tmp_gs_path,client)
        self.assertEqual(s,'JLPUSLMIHV')

    def test_gcp_file(self):
        client = gcstorage.client.Client()
        with tempfile.TemporaryDirectory() as tempdir:
            timestamp = int(time.time())
            src_fn = os.path.join('futsu','gcp','test','test_storage.txt')
            tmp_gs_path  = 'gs://futsu-test/test-CQJWTXYXEJ-{0}'.format(timestamp)
            tmp_filename = os.path.join(tempdir,'PKQXWFJWRB')
            
            fstorage.cp_local_to_gcp(src_fn,tmp_gs_path,client)
            fstorage.cp_gcp_to_local(tmp_gs_path,tmp_filename,client)
            
            self.assertFalse(ffs.diff(src_fn,tmp_filename))

    def test_exist(self):
        timestamp = int(time.time())
        tmp_gs_path  = 'gs://futsu-test/test-NKLUNOKTWZ-{0}'.format(timestamp)

        client = gcstorage.client.Client()
        self.assertFalse(fstorage.exist(tmp_gs_path,client))
        fstorage.set_string(tmp_gs_path,'DQJDDJMULZ',client)
        self.assertTrue(fstorage.exist(tmp_gs_path,client))

    def test_delete(self):
        timestamp = int(time.time())
        tmp_gs_path  = 'gs://futsu-test/test-EYVNPCTBAH-{0}'.format(timestamp)

        client = gcstorage.client.Client()

        self.assertFalse(fstorage.exist(tmp_gs_path,client))

        fstorage.rm(tmp_gs_path,client)

        self.assertFalse(fstorage.exist(tmp_gs_path,client))

        fstorage.set_string(tmp_gs_path,'BHAHMMJVYF',client)
        self.assertTrue(fstorage.exist(tmp_gs_path,client))

        fstorage.rm(tmp_gs_path,client)

        self.assertFalse(fstorage.exist(tmp_gs_path,client))
