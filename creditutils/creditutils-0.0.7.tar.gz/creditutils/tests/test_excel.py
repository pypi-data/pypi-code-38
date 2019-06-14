'''
Created on 2017年9月16日

@author: caifh
'''
import unittest
import os
import creditutils.excel_util as excel


class Test(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(__file__)

    def tearDown(self):
        pass

    def testLabelTable_get_label_index(self):
        filename = 'test.xlsx'
        file_path = os.path.join(self.dir, filename)
        table = excel.LabelTable(file_path)
        label = 'first'
        expected = 0
        actual = table.get_label_index(label)
        msg = 'expecting {}, but got {}!'.format(expected, actual)
        self.assertEqual(expected, actual, msg)

        label = 'second'
        expected = 1
        actual = table.get_label_index(label)
        msg = 'expecting {}, but got {}!'.format(expected, actual)
        self.assertEqual(expected, actual, msg)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testLabelTable_']
    unittest.main()
