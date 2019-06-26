# -*- coding: utf-8 -*-
import unittest
from os import path

from cpbox.tool import template
from cpbox.tool.testutils import RandomDir


class TestTempalte(unittest.TestCase, RandomDir):

    def setUp(self):
        RandomDir.setUp(self)
        self.template_dir = path.join(self.tests_root_dir, 'test-data')

    def tearDown(self):
        RandomDir.tearDown(self)

    def test_render_to_file(self):
        data = {'date': '20190520'}
        str_after_render = u'寒雨连江夜入吴 平明送客楚山孤 20190520'

        template_file = path.join(self.template_dir, 'test-template-unicode.jinja2')
        ret = template.render_to_str(template_file, data)
        self.assertEqual(ret, str_after_render)

        target_file = path.join(self.temp_dir, 'tmp')
        ret_from_file = template.render_to_file(template_file, data, target_file)
        self.assertEqual(ret_from_file, str_after_render)

if __name__ == '__main__':
    unittest.main()
