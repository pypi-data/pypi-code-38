"""
Tests for common cli functionality
"""
import unittest

import candig.common.cli as cli


class TestCli(unittest.TestCase):

    def testArgumentParser(self):
        parser = cli.createArgumentParser("test parser")
        subparsers = parser.add_subparsers(title='subparsers')
        subparserName = "test-subparser"
        subparser = cli.addSubparser(
            subparsers, subparserName, "test subparser")
        argumentName = 'argument'
        subparser.add_argument(argumentName)
        parser.parse_args([subparserName, argumentName])
