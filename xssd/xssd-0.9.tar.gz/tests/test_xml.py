"""
Test XML parsing ability.
"""

import os
from unittest import TestCase
from xssd.parse import ParseXML

PATH = os.path.dirname(__file__)

class TestXMLParse(TestCase):
    """Test loading of modules."""
    def setUp(self):
        self._parser = ParseXML(os.path.join(PATH, 'data/file3.xml'))

    def test_create_object(self):
        """Creation of ParserXML object"""
        self.assert_(self._parser)
        self.assert_(isinstance(self._parser, ParseXML))

    def test_getting_data(self):
        """Getting data from parser"""
        self.assert_(self._parser.data)

    def test_first_hash(self):
        """First hash level"""
        self.assert_(self._parser.data['input'])

    def test_second_hash(self):
        """Second hash level"""
        self.assertEqual(self._parser.data['input']['content'], "Too Short")

    def test_arrays(self):
        """Arrays of scalars"""
        self.assertEqual(self._parser.data['input']['edited'][0], '2007-11-01 20:23:12')

    def test_array_fill(self):
        """Array fills correctly"""
        self.assertEqual(self._parser.data['input']['edited'][3], '2007-11-04 20:23:12')

    def test_array_structure(self):
        """Arrays of structures"""
        self.assert_(isinstance(self._parser.data['input']['foo'], list))

    def test_first_element(self):
        """First structural array element"""
        self.assertEqual(self._parser.data['input']['foo'][0]['bar1'], 'A')

    def test_last_element(self):
        """Last structrural array element"""
        self.assertEqual(self._parser.data['input']['foo'][-1]['bar1'], 'E')
