#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
from pathlib import Path

from hyperdiary import parser, Diary
from hyperdiary.diary import find_ids, find_tags, tokenize


def in_test_folder(relative_path):
    return Path(__file__).parent / relative_path


class TestHyperdiary(unittest.TestCase):

    def test_command_line_interface(self):
        self.assertEqual('check', parser.parse_args(['check']).subcommand)
    
    def test_loading_of_entries(self):
        diary = Diary.discover(in_test_folder('src'))
        diary.load_entries()
        self.assertGreaterEqual(len(diary.entries), 3)
    
    def test_missing_hyperdiary_json(self):
        self.assertRaises(FileNotFoundError, Diary.discover,
                          path=in_test_folder('.'))

    def test_tokenization(self):
        line = '+tag A $test-line by $Jane_Doe|Jane; expect no content +hallo'
        self.assertEqual(2, len(find_tags(line)))
        self.assertEqual(2, len(find_ids(line)))
        self.assertEqual(7, len(list(tokenize(line))))
