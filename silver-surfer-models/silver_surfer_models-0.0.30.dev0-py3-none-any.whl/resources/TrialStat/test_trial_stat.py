import copy
import json
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.TrialStat import TrialStat


class TrialStatResourceTestCase(TestCase):
    def setUp(self):
        super(TrialStatResourceTestCase, self).setUp()
        self.inst = TrialStat()

        self.trial_stat1 = self.inst.create({
            'stat_type': 'aggregate',
            'name': 'instituted',
            'ref_counts_by_type': json.dumps({
                'EXHIBIT': 1,
                'FEDERAL_CASE': 2,
            }),
            'id_count': 123,
        })

        self.trial_stat2 = self.inst.create({
            'stat_type': 'trial',
            'name': 'IPR-101',
            'ref_counts_by_type': json.dumps({
                'EXHIBIT': 1,
                'FEDERAL_CASE': 2,
            }),
            'id_count': 34,
        })

        self.trial_stat3 = self.inst.create({
            'stat_type': 'tech_center',
            'name': '1600',
            'ref_counts_by_type': json.dumps({
                'EXHIBIT': 1,
                'FEDERAL_CASE': 22,
            }),
            'id_count': None,
        })

        self.valid_data = {
            'stat_type': 'aggregate',
            'name': 'denied',
            'ref_counts_by_type': json.dumps({
                'EXHIBIT': 1,
                'FEDERAL_CASE': 2,
            }),
            'id_count': 123,
        }

    @parameterized.expand([
        ('stat_type',),
        ('name',),
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
                'stat_type': self.trial_stat1['stat_type'],
                'name': self.trial_stat1['name'],
            },
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        second_equals_first(self.valid_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

    @parameterized.expand([
        ('id', 'trial_stat1', 'id', 1),
        ('stat_type', 'trial_stat1', 'stat_type', 1),
        ('name', 'trial_stat1', 'name', 1),
    ])
    def test_read_w_params(
        self,
        field_name,
        attr,
        attr_field,
        expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

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
        ('stat_type',),
        ('name',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.trial_stat1[field_name],
        })
        second_equals_first(
            self.trial_stat1,
            resp,
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'stat_type': self.valid_data['stat_type'],
            }
        )

    def test_upsert_creates_new_entry(self):
        data = copy.copy(self.valid_data)
        self.assertEqual(3, len(self.inst.read({})))
        self.inst.upsert(data)
        self.assertEqual(4, len(self.inst.read({})))

    def test_upsert_updates_existing_row(self):
        data = {
            **self.valid_data,
            **{
                'stat_type': self.trial_stat1['stat_type'],
                'name': self.trial_stat1['name'],
            },
        }
        self.assertEqual(3, len(self.inst.read({})))
        resp = self.inst.upsert(data)
        second_equals_first(
            data,
            resp,
        )
        self.assertEqual(3, len(self.inst.read({})))
