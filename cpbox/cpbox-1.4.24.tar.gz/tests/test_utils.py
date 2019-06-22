from os import path
import unittest

from cpbox.tool import file
from cpbox.tool import utils
from cpbox.tool.testutils import RandomDir

class TestUtils(unittest.TestCase, RandomDir):

    def setUp(self):
        RandomDir.setUp(self)
        self.template_dir = path.join(self.tests_root_dir, 'test-data')

    def tearDown(self):
        RandomDir.tearDown(self)

    def test_properties(self):
        dst_filename = path.join(self.temp_dir, 'out.properties')
        src_filename = path.join(self.template_dir, 'test-utils-properties.txt')
        ret = utils.load_properties(src_filename, to_dict=False)
        self.assertEqual(ret['VERSION_CODE'], '989')
        utils.dump_properties(ret, dst_filename)
        self.assertEqual(file.file_get_contents(dst_filename).strip(), file.file_get_contents(src_filename).strip())

if __name__ =='__main__':
    unittest.main()
