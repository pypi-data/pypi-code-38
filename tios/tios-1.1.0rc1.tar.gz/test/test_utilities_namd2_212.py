import unittest
from tios import utilities

class TestCheckGromacs514Methods(unittest.TestCase):

    def test_check__installed_version(self):
        result = utilities.installed_version('NAMD')
        self.assertEqual(result, '2.12')
