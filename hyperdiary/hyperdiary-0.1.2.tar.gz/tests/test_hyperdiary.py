#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

from hyperdiary import parser


class TestHyperdiary(unittest.TestCase):

    def test_command_line_interface(self):
        self.assertEqual('check', parser.parse_args(['check']).subcommand)
