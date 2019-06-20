
import os
import unittest

os.environ['UNICODE_CATEGORIES_CACHE'] = 'false'  # noqa

import unicategories as module
import unicategories_tools as tools


class TestAPI(unittest.TestCase):
    def test_public_api(self):
        self.assertIs(
            module.merge,
            tools.merge
            )
        self.assertIs(
            module.RangeGroup,
            tools.RangeGroup
            )
