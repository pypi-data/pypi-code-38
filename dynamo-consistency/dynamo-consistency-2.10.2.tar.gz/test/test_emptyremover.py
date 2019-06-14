#! /usr/bin/env python

import os
import sys
import time
import logging
import unittest

from dynamo_consistency import backend

# Get an accurate count, even if we do nothing
backend.registry.delete = lambda _, l: len(l)

from dynamo_consistency import datatypes
from dynamo_consistency.emptyremover import EmptyRemover

from base import TestBase


LOG = logging.getLogger(__name__)


class TestUnfilled(TestBase):
    # This is for testing the tree behavior when some of the DirectoryInfo.files is None
    empty = [
        'mc/ttThings/empty/dir/a',
        'mc/ttThings/empty/dir/b',
        'mc/ttThings/empty/dir2'
        ]

    unfilled = 'mc/ttThings/empty/unfilled'

    def do_more_setup(self):
        # Add empty files
        for d in self.empty:
            self.tree.get_node(d).add_files([]).mtime = 1

        self.tree.setup_hash()

        for d in ['', 'dir', 'dir/a', 'dir/b', 'dir2']:
            self.tree.get_node(os.path.join('mc/ttThings/empty', d), make_new=False).mtime = 1

        self.tree.setup_hash()

        LOG.debug(self.tree.displays())

    def test_count(self):
        # We want unfilled directories to not change the total count
        first_count = self.tree.count_nodes()
        self.assertTrue(self.tree.get_node(self.unfilled).files is None)
        self.assertEqual(first_count, self.tree.count_nodes())

    def test_empty_list(self):
        empty_list = self.tree.empty_nodes_list()

        self.assertTrue('/store/mc/ttThings/empty/dir/a' in empty_list)
        self.assertTrue('/store/mc/ttThings/empty' in empty_list)

        new_node = self.tree.get_node(self.unfilled)

        self.tree.setup_hash()
        new_list = self.tree.empty_nodes_list()

        self.assertFalse('/store/' + self.unfilled in new_list)
        self.assertFalse('/store/mc/ttThings/empty' in new_list)

    def test_delete_dir(self):
        first_count = self.tree.count_nodes(empty=True)
        self.assertRaises(datatypes.NotEmpty, self.tree.remove_node, '/store/mc/ttThings/empty/dir')
        self.tree.remove_node('/store/mc/ttThings/empty/dir/a')
        self.assertEqual(first_count - 1, self.tree.count_nodes(empty=True))
        self.assertFalse('/store/mc/ttThings/empty/dir/a' in self.tree.empty_nodes_list())

        # Check that self.files is None throws an exception
        new_node = self.tree.get_node(self.unfilled)
        new_node.mtime = time.time()
        self.assertRaises(datatypes.NotEmpty, self.tree.remove_node, '/store/' + self.unfilled)
        new_node.files = []
        # Still no good because of mtime
        self.assertRaises(datatypes.NotEmpty, self.tree.remove_node, '/store/' + self.unfilled)
        # Now it should delete just fine
        new_node.mtime = 1
        self.tree.remove_node('/store/' + self.unfilled)

    def test_big_removal(self):
        self.assertTrue(self.tree.empty_nodes_list())
        for d in self.tree.empty_nodes_list():
            self.tree.remove_node(d)
        self.assertFalse(self.tree.empty_nodes_list())

    def test_new_empty(self):
        # Piggy-backing setup to check a bug
        self.tree.get_node('mc/ttThings/empty').mtime = time.time()
        self.assertFalse('/store/mc/ttThings/empty' in self.tree.empty_nodes_list())

    def test_nontime_subdir(self):
        self.tree.get_node('mc/ttThings/empty/dir/a').mtime = None
        empties = self.tree.empty_nodes_list()
        self.assertFalse('/store/mc/ttThings/empty/dir/a' in empties)
        self.assertFalse('/store/mc/ttThings/empty' in empties)
        self.assertTrue('/store/mc/ttThings/empty/dir/b' in empties)

    def test_noself_stillempty(self):
        # There's some bug that is giving empty nodes back when it shouldn't
        # This is just me trying to hunt it down
        self.tree.get_node('mc/ttThings/empty/dir/a').mtime = time.time()
        self.tree.setup_hash()
        empties = self.tree.empty_nodes_list()
        self.assertFalse('/store/mc/ttThings/empty/dir/a' in empties)
        self.assertFalse('/store/mc/ttThings/empty' in empties)
        self.assertTrue('/store/mc/ttThings/empty/dir/b' in empties)

    def test_emptyremover(self):
        remover = EmptyRemover('test')
        before = self.tree.count_nodes()
        remover(self.tree)
        self.assertTrue(remover.get_removed_count())
        self.assertEqual(before, remover.get_removed_count() + self.tree.count_nodes())

    def test_empty_w_unfilled(self):
        remover = EmptyRemover('test')
        self.tree.get_node(self.unfilled)
        remover(self.tree)
        self.assertTrue(remover.get_removed_count())

    def test_empty_w_unfilled_diff_root(self):
        remover = EmptyRemover('test')
        self.tree.get_node(self.unfilled)
        self.tree.name = 'store'
        remover(self.tree)
        self.assertTrue(remover.get_removed_count())

class TestWeird(unittest.TestCase):
    def test_off_root(self):
        tree = datatypes.DirectoryInfo('mc')
        node = tree.get_node('test/an/empty')
        node.mtime = 1
        node.files = []
        tree.setup_hash()
        remover = EmptyRemover('test', lambda path: path == '/store/mc/test/an/empty')
        remover(tree)
        self.assertFalse(remover.get_removed_count())


if __name__ == '__main__':
    unittest.main()
