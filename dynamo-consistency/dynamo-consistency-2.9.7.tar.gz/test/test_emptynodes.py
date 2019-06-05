#! /usr/bin/env python

import unittest
import time

import base

class TestEmptyNode(base.TestBase):
    def do_more_setup(self):
        # New node, don't delete
        self.new = self.tree.get_node('empty')
        self.new.mtime = time.time()
        self.new.files = []
        # Old node, inside. Do delete
        self.old = self.tree.get_node('empty/node')
        self.old.mtime = 1
        self.old.files = []
        self.tree.setup_hash()

    def test_emptyset(self):
        self.assertEqual(len(self.tree.empty_nodes_set()), 1)
        self.assertEqual(self.tree.empty_nodes_list(), ['/store/empty/node'])
        # Make sure that we only get empty nodes if directory has been listed
        self.old.files = None
        self.assertFalse(self.tree.empty_nodes_set())


    def test_numfiles(self):
        self.assertEqual(self.old.get_num_files(place_new=False), 0)
        self.assertEqual(self.old.get_num_files(place_new=True), 0)
        self.assertEqual(self.new.get_num_files(place_new=False), 0)
        self.assertEqual(self.new.get_num_files(place_new=True), 1)

if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
