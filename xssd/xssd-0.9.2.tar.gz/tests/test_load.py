#!/usr/bin/python

import unittest
import sys
sys.path.insert(1, '../lib')

class TestLoad(unittest.TestCase):
    """Test loading of modules."""
    def test_base_module(self):
        import xssd

    def test_xsd_module(self):
        from xssd import Validator

    def test_xml_parser(self):
        from xssd.parse import ParseXML


