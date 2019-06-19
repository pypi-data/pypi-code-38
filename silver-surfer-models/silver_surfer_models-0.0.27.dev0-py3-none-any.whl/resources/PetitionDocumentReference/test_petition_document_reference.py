import copy

from marshmallow import ValidationError
from sqlalchemy.orm.exc import NoResultFound
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.Document import (
    Document,
)
from src.silver_surfer_models.resources.Trial import Trial
from src.silver_surfer_models.resources.PetitionDocumentReference import (
    PetitionDocumentReference,
)


class PetitionDocumentReferenceResourceTestCase(TestCase):
    def setUp(self):
        super(PetitionDocumentReferenceResourceTestCase, self).setUp()

        self.inst = PetitionDocumentReference()
        self.inst_trial = Trial()
        self.inst_document = Document()

        self.trial1 = self.inst_trial.create({
            'ptab_trial_num': 'CTA-101',
            'trial_filing_date': '2017-05-06',
            'patent_num': '9999',
            'is_cleaned': False,
            'is_processed': False,
        })
        self.trial2 = self.inst_trial.create({
            'ptab_trial_num': 'CTA-102',
            'trial_filing_date': '2017-05-06',
            'patent_num': '1000',
            'is_cleaned': False,
            'is_processed': False,
        })

        self.document1 = self.inst_document.create({
            'trial_id': self.trial1['id'],
            'ptab_document_id': 1111,
            'title': 'Inter Partes Review Petition of US 7879828',
        })

        self.petition_document_reference1 = self.inst.create({
            'document_id': self.document1['id'],
            'type': 'CIVIL_CASE',
            'value': '1:16-cv-00469 (filed Feb. 26, 2016)',
        })

        self.petition_document_reference2 = self.inst.create({
            'document_id': self.document1['id'],
            'type': 'FEDERAL_CASE',
            'value': 'Something else',
        })

        self.valid_data = {
            'document_id': self.document1['id'],
            'type': 'FEDERAL_CASE',
            'value': '778 F.3d 1271, 1279',
        }

    @parameterized.expand([
        ('document_id',),
        ('type',),
        ('value',),
    ])
    def test_create_validation_error_missing_field(self, field_to_pop):
        data = copy.copy(self.valid_data)
        data.pop(field_to_pop)
        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        second_equals_first(self.valid_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))

    @parameterized.expand([
        ('document_id', 'document1', 'id', 2),
        ('type', 'petition_document_reference1', 'type', 1),
        ('value', 'petition_document_reference1', 'value', 1),
    ])
    def test_read_w_params(
            self,
            field_name,
            attr,
            attr_field,
            expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

        resp = self.inst.read({
            field_name: getattr(self, attr)[attr_field],
        })
        self.assertEqual(expected_length, len(resp))

    @parameterized.expand([
        ('id', 999, NoResultFound),
    ])
    def test_one_raises_exception(self, field_name, field_value, exception):
        self.assertRaises(
            exception,
            self.inst.one,
            {
                field_name: field_value,
            },
        )

    @parameterized.expand([
        ('id',),
        ('type',),
        ('value',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.petition_document_reference1[field_name],
        })
        second_equals_first(
            self.petition_document_reference1,
            resp,
        )

    def test_delete_not_found(self):
        invalid_id = 99999
        self.assertRaises(
            NoResultFound,
            self.inst.delete,
            invalid_id,
        )

    def test_delete(self):
        response = self.inst.one({
            'id': self.petition_document_reference1['id'],
        })
        self.inst.delete(id=response['id'])
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': self.petition_document_reference1['id']},
        )

    def test_bulk_delete(self):
        response = self.inst.read({})
        self.assertEqual(2, len(response))

        self.inst.bulk_delete(document_id=self.document1['id'])

        response = self.inst.read({})
        self.assertEqual(0, len(response))
