import copy
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.Company import Company


class CompanyResourceTestCase(TestCase):
    def setUp(self):
        super(CompanyResourceTestCase, self).setUp()
        self.inst = Company()

        self.company1 = self.inst.create({
            'applicant_full_name': 'VALEANT PHARMACEUTICALS INTERNATIONAL',
            'exchange': 'NYSE',
            'parent_company': 'Bausche Health',
            'ticker': 'BHC',
        })

        self.company2 = self.inst.create({
            'applicant_full_name': 'PERRIGO UK FINCO LTD PARTNERSHIP',
            'exchange': 'NYSE',
            'parent_company': 'Perrigo',
            'ticker': 'PRGO',
        })

        self.valid_data = {
            'applicant_full_name': 'TARO PHARMACEUTICAL INDUSTRIES LTD',
            'exchange': 'NYSE',
            'parent_company': 'Taro Pharmaceuticals',
            'ticker': 'TARO',
        }

    @parameterized.expand([
        ('applicant_full_name',),
    ])
    def test_create_validation_error_missing_field(self, field_to_pop):
        base_data = copy.copy(self.valid_data)
        base_data.pop(field_to_pop)
        self.assertRaises(
            ValidationError,
            self.inst.create,
            base_data,
        )

    def test_create_violates_unique_constraint(self):
        self.assertRaises(
            IntegrityError,
            self.inst.create,
            {'applicant_full_name': self.company1['applicant_full_name']},
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        second_equals_first(self.valid_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))

    @parameterized.expand([
        ('id', 'company1', 'id', 1),
        ('applicant_full_name', 'company1', 'applicant_full_name', 1),
        ('parent_company', 'company1', 'parent_company', 1),
        ('ticker', 'company1', 'ticker', 1),
    ])
    def test_read_w_params(
        self,
        field_name,
        attr,
        attr_field,
        expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))

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
        ('applicant_full_name',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.company1[field_name],
        })
        second_equals_first(
            self.company1,
            resp,
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'exchange': self.valid_data['exchange'],
            }
        )

    def test_upsert_creates_new_entry(self):
        data = copy.copy(self.valid_data)
        self.assertEqual(2, len(self.inst.read({})))
        self.inst.upsert(data)
        self.assertEqual(3, len(self.inst.read({})))

    def test_upsert_updates_existing_row(self):
        data = {
            **self.valid_data,
            **{'applicant_full_name': self.company1['applicant_full_name']},
        }
        resp = self.inst.upsert(data)
        second_equals_first(
            data,
            resp,
        )
        self.assertEqual(2, len(self.inst.read({})))
