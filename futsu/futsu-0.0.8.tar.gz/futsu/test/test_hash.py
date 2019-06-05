from unittest import TestCase
import futsu.hash as hash
import tempfile
import os

class TestFs(TestCase):

    def test_md5_str(self):
        self.assertEqual(hash.md5_str('asdf'),'912ec803b2ce49e4a541068d495ab570')
        self.assertEqual(hash.md5_str(''),'d41d8cd98f00b204e9800998ecf8427e')
