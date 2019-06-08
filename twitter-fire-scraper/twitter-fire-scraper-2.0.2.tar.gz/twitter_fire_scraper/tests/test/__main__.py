import __init__

import os
import sys
import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()

    # Load current directory
    suite = loader.discover(os.path.abspath(os.path.dirname(__file__)))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
