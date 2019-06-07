# coding=utf-8

import unittest

from bdacore.text.utils import normalize_text
from future.utils import python_2_unicode_compatible


@python_2_unicode_compatible
class CleanData(unittest.TestCase):
    def test_normalize_text(self):
        # given
        input_string = u'Test 8, éèëùûàâïôöÎ ; \'!!!! ?;:'

        # when
        output_string = normalize_text(input_string)

        # then
        expected_string = "test 8 eeeuuaaiooi"
        self.assertEqual(expected_string, output_string)
