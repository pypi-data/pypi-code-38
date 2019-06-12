
import os

from .base_tests import BaseFileTest

PATH = os.path.dirname(__file__)

class JsonSetsTest(BaseFileTest):
    """Test JSON data files"""
    definition = os.path.join(PATH, 'data/definition1.json')

    def test_file1(self):
        """Positive Python File"""
        self.positive_test(os.path.join(PATH, 'data/file1.json'))

    def test_file2(self):
        """Negative Python File"""
        self.negative_test(os.path.join(PATH, 'data/file2.json'), None)


class XmlSetsTest(BaseFileTest):
    """Test xml data files"""
    definition = os.path.join(PATH, 'data/definition1.xsd')

    def test_file1(self):
        """Positive XML File"""
        self.positive_test(os.path.join(PATH, 'data/file1.xml'))

    def test_file2(self):
        """Negative XML File"""
        self.negative_test(os.path.join(PATH, 'data/file2.xml'), None)
