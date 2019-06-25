import copy
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.InstitutionProbability import (
    InstitutionProbability,
)


class InstitutionProbabilityResourceTestCase(TestCase):
    def setUp(self):
        super(InstitutionProbabilityResourceTestCase, self).setUp()
        self.inst = InstitutionProbability()

        self.ip1 = self.inst.create({
            'ptab_trial_num': 'IPR101',
            'is_instituted': True,
            'probability_of_institution': 0.345,
            'probability_end_before_trial_end': 0.42,
            'probability_of_all_claims_instituted': 0.345,
            'probability_of_some_claims_instituted': 0.65,
        })

        self.ip2 = self.inst.create({
            'ptab_trial_num': 'IPR201',
            'is_instituted': False,
            'probability_of_institution': 0.43,
            'probability_end_before_trial_end': 0.41,
            'probability_of_all_claims_instituted': 0.34,
            'probability_of_some_claims_instituted': 0.74,
        })

        self.valid_data = {
            'ptab_trial_num': 'IPR301',
            'is_instituted': True,
            'probability_of_institution': 0.45,
            'probability_end_before_trial_end': 0.39,
            'probability_of_all_claims_instituted': 0.4,
            'probability_of_some_claims_instituted': 0.86,
        }

    @parameterized.expand([
        ('ptab_trial_num',),
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
                **self.valid_data,
                **{'ptab_trial_num': self.ip1['ptab_trial_num']},
            }
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        second_equals_first(self.valid_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))

    @parameterized.expand([
        ('id', 'ip1', 'id', 1),
        ('ptab_trial_num', 'ip1', 'ptab_trial_num', 1),
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
        ('ptab_trial_num',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.ip1[field_name],
        })
        second_equals_first(
            self.ip1,
            resp,
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'is_instituted': False,
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
            **{
                'ptab_trial_num': self.ip1['ptab_trial_num'],
                'is_instituted': not self.ip1['is_instituted'],
            },
        }
        self.assertEqual(2, len(self.inst.read({})))
        resp = self.inst.upsert(data)
        second_equals_first(
            data,
            resp,
        )
        self.assertEqual(2, len(self.inst.read({})))
