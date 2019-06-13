import sys
import unittest
from unittest.mock import patch

from mungo.cli import main


class TestPackageSplitting(unittest.TestCase):
    def test_profile_create(self):
        with patch.object(sys, 'argv', ["mungo", "create", "-n", "foo", "snakemake", "--dryrun"]):
            print(sys.argv)
            main()


if __name__ == '__main__':
    unittest.main()
