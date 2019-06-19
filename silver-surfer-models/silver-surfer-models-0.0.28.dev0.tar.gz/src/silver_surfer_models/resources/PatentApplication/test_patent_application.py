import copy
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.PatentApplication import PatentApplication


class PatentApplicationResourceTestCase(TestCase):
    def setUp(self):
        super(PatentApplicationResourceTestCase, self).setUp()
        self.inst = PatentApplication()

        self.patent_application1 = self.inst.create({
            'application_number': '1000',
            'jurisdiction': 'USPAT',
        })

        self.patent_application2 = self.inst.create({
            'application_number': '2000',
            'jurisdiction': 'USPAT',
        })

        self.valid_data = {
            'application_number': '3000',
            'jurisdiction': 'USPAT',
        }

    @parameterized.expand([
        ('application_number',),
        ('jurisdiction',),
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
            {
                'application_number': (
                    self.patent_application1['application_number']),
                'jurisdiction': self.patent_application1['jurisdiction'],
            },
        )

    def test_create(self):
        data = copy.copy(self.valid_data)
        resp = self.inst.create(data)
        second_equals_first(data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

    @parameterized.expand([
        ('id', 'patent_application1', 'id', 1),
        ('application_number', 'patent_application1', 'application_number', 1),
        ('jurisdiction', 'patent_application1', 'jurisdiction', 2),
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
        ('jurisdiction', 'USPAT', MultipleResultsFound),
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
        ('application_number',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.patent_application1[field_name],
        })
        second_equals_first(
            self.patent_application1,
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
        response = self.inst.one({'id': self.patent_application1['id']})
        self.inst.delete(id=response['id'])
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': self.patent_application1['id']},
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'application_number': self.valid_data['application_number'],
            }
        )

    def test_upsert_creates_new_entry(self):
        data = copy.copy(self.valid_data)
        self.assertEqual(2, len(self.inst.read({})))
        self.inst.upsert(data)
        self.assertEqual(3, len(self.inst.read({})))

    def test_upsert_updates_existing_row(self):
        data = {
            'application_number': (
                self.patent_application1['application_number']),
            'jurisdiction': self.patent_application1['jurisdiction'],
            'abstract_text': 'Something',
        }
        resp = self.inst.upsert(data)
        second_equals_first(
            data,
            resp,
        )
        self.assertEqual(2, len(self.inst.read({})))
