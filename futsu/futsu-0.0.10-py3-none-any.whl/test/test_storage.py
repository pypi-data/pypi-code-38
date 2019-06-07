from unittest import TestCase
import futsu.storage as storage
import tempfile
import os
import futsu.fs as fs
import time

class TestStorge(TestCase):

    def test_local(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir,'QKDQXVOOME')
            src_file = os.path.join('futsu','test','test_storage_0.txt')
            
            storage.local_to_path(tmp_filename,src_file)
            
            self.assertFalse(fs.diff(tmp_filename,src_file))

    def test_gcp(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir,'GPVRUHXTTC')
            src_file = os.path.join('futsu','test','test_storage_0.txt')
            timestamp = int(time.time())
            tmp_gs_blob = 'gs://futsu-test/test-NXMUHBDEMR-{0}'.format(timestamp)
            
            storage.local_to_path(tmp_gs_blob,src_file)
            storage.path_to_local(tmp_filename,tmp_gs_blob)
            
            self.assertFalse(fs.diff(tmp_filename,src_file))
