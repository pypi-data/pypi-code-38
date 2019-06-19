from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)
from sqlalchemy.exc import IntegrityError
from parameterized import parameterized
from marshmallow import ValidationError

from src.silver_surfer_models.resources.Claim import (
    Claim,
)
from test.mixins.BasicDataMixin import BasicDataMixin
from test.backendtestcase import TestCase
from test.utils import second_equals_first


class ClaimResourceTestCase(BasicDataMixin, TestCase):
    def setUp(self):
        super(ClaimResourceTestCase, self).setUp()
        self.inst = Claim()
        self.claim1 = self.inst.create({
            'patent_id': self.patent1['id'],
            'claim_number': 1,
            'claim_text': 'Some claim 1',
        })
        self.claim2 = self.inst.create({
            'patent_application_id': self.patent_application1['id'],
            'claim_number': 1,
            'claim_text': 'Some claim 2',
        })
        self.claim3 = self.inst.create({
            'patent_application_id': self.patent_application2['id'],
            'claim_number': 2,
            'claim_text': 'Some claim 3',
        })

    def _get_dict_with_fields(self, base_data, fields_to_keep):
        data = {}
        for key in base_data:
            if key in fields_to_keep:
                data[key] = base_data[key]
        return data

    @parameterized.expand([
        (['claim_number', 'claim_text'],),
    ])
    def test_create_validation_error_missing_field(self, fields_to_keep):
        base_data = {
            'patent_id': self.patent1['id'],
            'patent_application_id': self.patent_application1['id'],
            'claim_number': 100,
            'claim_text': 'Some claim 100',
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)

        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    def test_create_validation_error_both_fields(self):
        data = {
            'patent_id': self.patent1['id'],
            'patent_application_id': self.patent_application1['id'],
            'claim_number': 100,
            'claim_text': 'Some claim 100',
        }
        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        (['claim_number', 'claim_text', 'patent_id'], 'claim1'),
        (['claim_number', 'claim_text', 'patent_application_id'], 'claim2'),
    ])
    def test_create_violates_unique_constraint(
        self,
        fields_to_keep,
        attr_claim,
    ):
        existing_claim = getattr(self, attr_claim)
        base_data = {
            'patent_id': self.patent1['id'],
            'patent_application_id': self.patent_application1['id'],
            'claim_number': existing_claim['claim_number'],
            'claim_text': existing_claim['claim_text'],
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)

        self.assertRaises(
            IntegrityError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        ('patent_id', ['claim_number', 'claim_text', 'patent_id']),
        (
            'patent_application_id',
            ['claim_number', 'claim_text', 'patent_application'],
        ),
    ])
    def test_create_violates_fk_constraint(
        self,
        field_to_test,
        fields_to_keep,
    ):
        base_data = {
            'patent_id': self.patent1['id'],
            'patent_application_id': self.patent_application1['id'],
            'claim_number': 123,
            'claim_text': 'Some claim 123',
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)
        data[field_to_test] = 999

        self.assertRaises(
            IntegrityError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        (['claim_number', 'claim_text', 'patent_id'],),
        (['claim_number', 'claim_text', 'patent_application_id'],),
    ])
    def test_create(self, fields_to_keep):
        base_data = {
            'patent_id': self.patent1['id'],
            'patent_application_id': self.patent_application1['id'],
            'claim_number': 123,
            'claim_text': 'Some claim 123',
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)
        resp = self.inst.create(data)
        second_equals_first(data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

    @parameterized.expand([
        ('patent_id', 'claim1', 1),
        ('patent_application_id', 'claim2', 1),
        ('claim_number', 'claim3', 1),
    ])
    def test_read_with_params(self, query_field, attr_claim, expected_length):
        resp = self.inst.read({
            query_field: getattr(self, attr_claim)[query_field],
        })
        self.assertEqual(expected_length, len(resp))

    def test_one_raises_no_result_found_exception(self):
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': 9999},
        )

    def test_one_raises_multiple_results_found_exception(self):
        self.assertRaises(
            MultipleResultsFound,
            self.inst.one,
            {'claim_number': self.claim1['claim_number']},
        )

    @parameterized.expand([
        ('id', 'claim1'),
        ('patent_id', 'claim1'),
        ('patent_application_id', 'claim2'),
        ('claim_number', 'claim3'),
    ])
    def test_one(self, field_name, attr):
        related_matter = getattr(self, attr)
        resp = self.inst.one({
            field_name: related_matter[field_name],
        })
        second_equals_first(
            related_matter,
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
        response = self.inst.one({'id': self.claim1['id']})
        self.inst.delete(id=response['id'])
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': self.claim1['id']},
        )
