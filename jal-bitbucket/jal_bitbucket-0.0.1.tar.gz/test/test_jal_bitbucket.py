import json
import unittest
import types

from bitbucket import bitbucket


class TestBitBucket(unittest.TestCase):
    """Test bitbucket.py"""
    def setUp(self):
        self.bitbucket = bitbucket.BitBucket()

    def test_repr(self):
        """Test __repr__ method"""
        self.assertTrue(isinstance(self.bitbucket, str))
