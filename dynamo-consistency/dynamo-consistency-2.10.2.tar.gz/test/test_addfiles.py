#! /usr/bin/env python

import unittest

from dynamo_consistency.datatypes import DirectoryInfo


FILES = [('/store/b/test.root', 1),
         ('/store/a/test.root', 1),
         ('/store/b/test23.root', 1)]

def files():
    for name, size in FILES:
        yield name, size, 100


class TestAdd(unittest.TestCase):
    def test_order(self):
        t1 = DirectoryInfo('/store')
        t2 = DirectoryInfo('/store')

        t1.add_file_list(files())
        t2.add_file_list(sorted(files()))

        self.assertFalse(files() == sorted(files()))
        self.assertFalse(t1.hash)
        self.assertFalse(t2.hash)
        t1.setup_hash()
        t2.setup_hash()

        self.assertEqual(t1.hash, t2.hash)

        self.assertEqual(len(t1.get_files()), len(FILES))


if __name__ == '__main__':
    unittest.main()
