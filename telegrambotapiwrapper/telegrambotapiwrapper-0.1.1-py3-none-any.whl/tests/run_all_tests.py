import os
import unittest
if __name__ == '__main__':
    loader = unittest.TestLoader()
    dir_ = os.path.dirname(__file__)
    suite = loader.discover(dir_, 'test_*')

    runner = unittest.TextTestRunner()
    runner.run(suite)