import unittest
from tios import utilities

class TestCheckGromacs2018Methods(unittest.TestCase):

    def test_check_gromacs_installed_version(self):
        result = utilities.installed_version('GROMACS')
        self.assertNotEqual(result, None)
