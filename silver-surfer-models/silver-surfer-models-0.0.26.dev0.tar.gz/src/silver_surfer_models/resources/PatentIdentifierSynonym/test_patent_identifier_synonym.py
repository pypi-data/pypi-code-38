from marshmallow import ValidationError
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.PatentIdentifierSynonym import (
    PatentIdentifierSynonym,
)
from src.silver_surfer_models.resources.Patent import Patent


class PatentIdentifierSynonymResourceTestCase(TestCase):
    def setUp(self):
        super(PatentIdentifierSynonymResourceTestCase, self).setUp()
        self.inst_patent = Patent()
        self.inst = PatentIdentifierSynonym()
        self.patent1 = self.inst_patent.create({
            'patent_number': '1000',
            'app_grp_art_number': '5000',
            'jurisdiction': 'USPAT',
        })
        self.patent2 = self.inst_patent.create({
            'patent_number': '2000',
            'app_grp_art_number': '5000',
            'jurisdiction': 'USPAT',
        })
        self.patent_identifier_synonym1 = self.inst.create({
            'patent_id': self.patent1['id'],
            'synonym': 'some synonym',
        })

    def test_create_validation_error_missing_fields(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {},
        )

    def test_create_validation_error_blank_synonym(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {
                'patent_id': 123,
                'synonym': '',
            },
        )

    def test_create_duplicate_patent_id(self):
        self.assertRaises(
            Exception,
            self.inst.create,
            {
                'patent_id': self.patent_identifier_synonym1['patent_id'],
                'synonym': self.patent_identifier_synonym1['synonym'],
            }
        )

    def test_create(self):
        new_data = {
            'patent_id': self.patent2['id'],
            'synonym': 'some synonym',
        }
        response = self.inst.create(new_data)
        second_equals_first(new_data, response)

    def test_read_validation_error_blank_synonym(self):
        self.assertRaises(
            ValidationError,
            self.inst.read,
            {'synonym': ''},
        )

    def test_read_all(self):
        response = self.inst.read({})
        self.assertEqual(len(response), 1)

    def test_read_w_params(self):
        # setup
        self.inst.create({
            'patent_id': self.patent1['id'],
            'synonym': 'some synonym2',
        })
        self.inst.create({
            'patent_id': self.patent2['id'],
            'synonym': self.patent_identifier_synonym1['synonym'],
        })

        response = self.inst.read({})
        self.assertEqual(len(response), 3)

        response = self.inst.read({
            'synonym': self.patent_identifier_synonym1['synonym']
        })
        self.assertEqual(len(response), 2)

    def test_one_raises_MultipleResultsFound(self):
        # setup
        self.inst.create({
            'patent_id': self.patent2['id'],
            'synonym': self.patent_identifier_synonym1['synonym'],
        })

        self.assertRaises(
            MultipleResultsFound,
            self.inst.one,
            {'synonym': self.patent_identifier_synonym1['synonym']},
        )

    def test_one_raises_NoResultFound(self):
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'synonym': '123123'},
        )
