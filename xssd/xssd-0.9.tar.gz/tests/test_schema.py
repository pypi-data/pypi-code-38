"""
Test xml schema files.
"""

import os

from xssd.errors import (
    NO_ERROR, INVALID_EXIST
)
from .base_tests import BaseFileTest

PATH = os.path.dirname(__file__)

class TestSelfSchema(BaseFileTest):
    """Test xml data files"""
    definition = os.path.join(PATH, 'data/schema.xsd')

    def _schema_test(self, filename):
        self.positive_test(filename)

    def test_00_smallest(self):
        """Validate Smallest"""
        self._schema_test(os.path.join(PATH, 'data/smallest.xsd'))

    def test_01_definition_zero(self):
        """Validate Simplest"""
        self._schema_test(os.path.join(PATH, 'data/definition0.xsd'))

    def test_02_definition_one(self):
        """Validate Schema One"""
        self._schema_test(os.path.join(PATH, 'data/definition1.xsd'))

    def test_02_definition_two(self):
        """Validate Schema Two"""
        self._schema_test(os.path.join(PATH, 'data/definition2.xsd'))

    def test_04_broken_schema(self):
        """Invalidate Schema"""
        errors = {u'schema': {
            u'complexType': [
                {u'attribute': NO_ERROR, u'_name': NO_ERROR, u'_bogus': INVALID_EXIST,
                 u'or': NO_ERROR, u'element': NO_ERROR},
                {u'attribute': NO_ERROR, u'_name': NO_ERROR, u'xor': INVALID_EXIST,
                 u'or': NO_ERROR, u'element': NO_ERROR},
                {u'attribute': NO_ERROR, u'_type': INVALID_EXIST, u'_name': NO_ERROR,
                 u'or': NO_ERROR, u'element': NO_ERROR}
            ],
            u'simpleType': NO_ERROR, u'element': NO_ERROR, 'annotation': NO_ERROR,
            }}
        self.negative_test(os.path.join(PATH, 'data/broken.xsd'), errors)

    def test_20_self_validate(self):
        """Self Validation"""
        self._schema_test(os.path.join(PATH, 'data/schema.xsd'))
