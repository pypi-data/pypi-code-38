# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest
from unittest import mock

from upt import checksum


@mock.patch('builtins.open', new_callable=mock.mock_open, read_data=b'foobar')
class TestChecksum(unittest.TestCase):
    MD5 = '3858f62230ac3c915f300c664312c63f'
    SHA256 = 'c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2'
    SHA256_BASE64 = 'w6uP8Tcg6K2QR905Rms8iXTlksL6OD1KOWBxTK7wxPI='

    def setUp(self):
        self.path = '/fake/path'

    def test_md5_checksum(self, open_fn):
        self.assertEqual(checksum._compute_md5_checksum(self.path), self.MD5)

    def test_sha256_checksum(self, open_fn):
        self.assertEqual(checksum._compute_sha256_checksum(self.path),
                         self.SHA256)

    def test_sha256_base64_checksum(self, open_fn):
        self.assertEqual(checksum._compute_sha256_base64_checksum(self.path),
                         self.SHA256_BASE64)

    def test_compute_checksum(self, open_fn):
        self.assertEqual(checksum.compute_checksum(self.path, 'md5'), self.MD5)

    def test_compute_checksum_invalid_hash(self, open_fn):
        error = 'Unknown hash "fake-hash"'
        with self.assertRaisesRegex(checksum.HashUnknown, error):
            checksum.compute_checksum(self.path, 'fake-hash')

    @mock.patch('hashlib.new', side_effect=ValueError)
    def test_compute_checksum_unavailable_hash(self, hash_fn, open_fn):
        error = 'Hash "rmd160" is not available on your system'
        with self.assertRaisesRegex(checksum.HashUnavailable, error):
            checksum.compute_checksum(self.path, 'rmd160')
