# -*- coding: utf-8 -*-
import unittest
import tempfile
import sys
from os import path

import shutil

from cpbox.tool import template
from cpbox.tool import file
from cpbox.tool import strings

from cpbox.tool.testutils import RandomDir

class TestTempalte(unittest.TestCase, RandomDir):

    def setUp(self):
        RandomDir.setUp(self)
        self.template_dir = path.join(self.tests_root_dir, 'test-data')

    def tearDown(self):
        RandomDir.tearDown(self)

    def test_write(self):
        import six
        target_file = path.join(self.temp_dir, self.random_str(10))
        strs = ['b', u'b', '好', u'好']
        for s in strs:
            file.file_put_contents(target_file, s)
            ret = file.file_get_contents(target_file)
            if six.PY2:
                self.assertEqual(type(ret), unicode)
            else:
                self.assertEqual(type(ret), str)

if __name__ == '__main__':
    unittest.main()
