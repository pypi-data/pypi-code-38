import unittest
import os
import sys
import ntpath


def run(test_name='all'):
    loader = unittest.TestLoader()
    head, tail = ntpath.split(os.path.realpath(__file__))
    sys.path.append(head)
    start_dir = head + '/tests'
    if test_name == 'all':
        suite = loader.discover(start_dir)

    else:
        suite = loader.discover(start_dir, test_name + '*')
    runner = unittest.TextTestRunner()
    runner.run(suite)
