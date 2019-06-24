
# encoding: utf-8
import unittest

from hyperstools.ssh import SSH

class TestHyperstools(unittest.TestCase):
    """Tests for `hyperstools` package."""

    def setUp(self):
        self.client = SSH(username='root', password='redhat', hostname='10.123.1.119')


    def test_000_something(self):
        """Test something."""
        self.client.exec('ls -l')
