# -*- coding: utf-8 -*-


import os
import unittest

case_path = '.' 

def all_cases():
    discover = unittest.defaultTestLoader.discover(case_path, 
            pattern='test_*.py', top_level_dir=None)
    for case in discover:
        print 'CASE: %s' % case
    print '\n'
    return discover


if __name__ == '__main__':
    print '--------------- RUN UNIT TEST CASES ----------------'
    runner = unittest.TextTestRunner()
    runner.run(all_cases())
