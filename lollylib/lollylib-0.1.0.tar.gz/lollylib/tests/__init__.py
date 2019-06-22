"""
Tests are an essential part of lollylib and are shipped with it.
One way to run tests in python 3:
    import lollylib.test as test
    test.run()
Read library documentation for more info.
Tests create and delete temporary directory '~tmp_test_lollylib' in user home directory.
Sometimes, if the tests fail, this directory may remain on your hard drive
and you need to delete it manually.
"""
import os
import sys
import ntpath

"""
Following code adds parent directory of this file to sys.path so that
all python files in the parent directory can be directly imported by tests.
Thus, the tests will always use library version
located in their parent dir.
"""

head, tail = ntpath.split(os.path.realpath(__file__))
sys.path.append(os.path.dirname(head))
