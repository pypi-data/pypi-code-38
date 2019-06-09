#! /usr/bin/env python

import os
import unittest

import base

from dynamo_consistency.backend.filereader import file_reader

class TestFileDump(base.TestBase):
    def test_filedump(self):
        tree = file_reader('txtfiles/filedump.txt', lambda line: (line.split()[0], int(line.split()[2])))

        self.check_equal(self.tree, tree)

if __name__ == '__main__':
    unittest.main()
