#! /usr/bin/env python

import re
import unittest

from dynamo_consistency import backend

class TestBackendDocs(unittest.TestCase):
    def test_provides_docs(self):
        lines = backend.__doc__.split('\n')
        for index, line in enumerate(lines):
            if re.match('^-+$', line):
                self.assertTrue(re.search('::\s%s\\b' % lines[index-1], lines[index + 2]))


if __name__ == '__main__':
    unittest.main()
