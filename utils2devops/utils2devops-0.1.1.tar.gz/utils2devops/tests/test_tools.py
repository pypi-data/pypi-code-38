import unittest
from unittest import TestCase

from utils2devops.tools.description import get_long_description_from_file
from utils2devops.tools.single_sourcing_package_version import get_version


class BasicTestCase(TestCase):

    def test_get_long_description_from_file(self):
        # nominal
        path = './docs/'
        filename = 'version.py'
        r = get_long_description_from_file(path, filename)
        self.assertEqual(r, '__version__ = \'0.1.1\'')
        # fault
        r = get_long_description_from_file(path, 'notExist')
        self.assertEqual(
            r,
            'get_long_description_from_file: No such file or directory'
        )

    def test_get_version(self):
        # nominal
        r = get_version('./docs/')
        self.assertEqual(r, '0.1.1')
        # fault
        r = get_version('notExist')
        self.assertEqual(
            r,
            'get_version: No such file or directory'
        )


if __name__ == '__main__':
    unittest.main()
