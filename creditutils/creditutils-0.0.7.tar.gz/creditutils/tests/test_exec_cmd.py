'''
Created on 2017年8月2日

@author: caifh
'''
import unittest
import creditutils.exec_cmd as exec_cmd


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


def test_run_cmd_for_code_in_specified_dir():
    dst_dir = '/Users/caifh/Documents/temp'
    cmd_str = 'ls'
    rtn_code = exec_cmd.run_cmd_for_code_in_specified_dir(dst_dir, cmd_str, print_flag=True)
    print('rtn_code: {}'.format(rtn_code))


def test_run_cmd_for_output_in_specified_dir():
    dst_dir = '/Users/caifh/Documents/temp'
    cmd_str = 'ls'
    rtn_str = exec_cmd.run_cmd_for_output_in_specified_dir(dst_dir, cmd_str, print_flag=True)
    print('rtn_str: {}'.format(rtn_str))


def test_main():
    #     test_run_cmd_for_code_in_specified_dir()
    test_run_cmd_for_output_in_specified_dir()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()

    test_main()
