import unittest

import pycodestyle


class TestCodeFormat(unittest.TestCase):

    def test_conformance(self):
        """Test that we conform to PEP-8."""
        style = pycodestyle.StyleGuide()
        result = style.check_files(['ems_r25'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")
