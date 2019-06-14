import json
import unittest
import types

from jal_bitbucket import bitbucket


class TestBitBucket(unittest.TestCase):
    """Test bitbucket.py"""
    def setUp(self):
        self.bitbucket = bitbucket.BitBucket()

    def test_repr(self):
        """Test __repr__ method"""
        print(type(self.bitbucket))
        self.assertTrue(isinstance(repr(self.bitbucket), str))
