import re

from unittest import TestCase
from unittest.mock import patch

from crossref_commons.relations import get_alias, get_related
from crossref_commons.types import RelationType


class RelationTestCase(TestCase):
    def test_get_alias_empty(self):
        with self.assertRaises(ValueError) as context:
            get_alias(None)
        self.assertTrue('None' in context.exception.args[0])

        with self.assertRaises(ValueError) as context:
            get_alias('not-a-doi')
        self.assertTrue('not-a-doi' in context.exception.args[0])

    def test_get_alias(self):
        self.assertIsNone(get_alias('10.5621/sciefictstud.40.2.0382'))
        self.assertIsNotNone(
            re.match('10.\d{4,9}/[\-\._;\(\)\/:A-Z0-9]+',
                     get_alias('10.1037//0022-3514.62.3.434')))


class RelationEntityTestCase(TestCase):
    @patch('crossref_commons.relations.get_alias')
    def test_get_entity_alias(self, mock_fun):
        get_related('10.1037//0022-3514.62.3.434', RelationType.ALIAS)
        mock_fun.assert_called_once_with('10.1037//0022-3514.62.3.434')

    @patch('crossref_commons.relations.get_alias')
    def test_get_entity_bad_type(self, *mocks):
        with self.assertRaises(ValueError) as context:
            get_related('id', 'not-a-re-type')
        for m in mocks:
            m.assert_not_called()
        self.assertTrue('not-a-re-type' in context.exception.args[0])
