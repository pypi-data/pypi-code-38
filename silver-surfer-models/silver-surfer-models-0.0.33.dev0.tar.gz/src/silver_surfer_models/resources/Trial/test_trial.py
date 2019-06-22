from marshmallow import ValidationError
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)
from sqlalchemy.exc import IntegrityError
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.Trial import (
    Trial,
    TrialNotFoundException,
)


class TrialResourceTestCase(TestCase):
    def setUp(self):
        super(TrialResourceTestCase, self).setUp()
        self.inst = Trial()

        self.trial1 = self.inst.create({
            'ptab_trial_num': 'CTA-101',
            'trial_filing_date': '2017-05-06',
            'patent_num': '9999',
            'is_cleaned': False,
            'is_processed': False,
        })

    def test_create_validation_error_no_ptab(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {},
        )

    def test_create_validation_error_no_trial_filing_date(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {
                'ptab_trial_num': 'CTA-102',
            },
        )

    def test_create_validation_error_no_patent_num(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {
                'ptab_trial_num': 'CTA-102',
                'trial_filing_date': '2017-05-06',
            },
        )

    def test_create_duplicate_ptab_trial_num(self):
        self.assertRaises(
            IntegrityError,
            self.inst.create,
            {
                'ptab_trial_num': 'CTA-101',
                'trial_filing_date': '2017-05-06',
                'patent_num': '1234',
                'is_cleaned': False,
                'is_processed': False,
            },
        )

    def test_create(self):
        data = {
            'ptab_trial_num': 'CTA-102',
            'trial_filing_date': '2017-05-06',
            'patent_num': '8888',
            'is_cleaned': False,
            'is_processed': False,
        }
        response = self.inst.create(data)
        second_equals_first(
            {
                'ptab_trial_num': data['ptab_trial_num'],
                'trial_filing_date': '2017-05-06T00:00:00+00:00',
                'patent_num': data['patent_num']
            },
            response,
        )

    def test_read_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.read,
            {'ptab_trial_num': ''},
        )

    def test_read_all(self):
        # setup
        self.inst.create({
            'ptab_trial_num': 'CTA-102',
            'trial_filing_date': '2017-05-06',
            'patent_num': '1111',
            'is_cleaned': False,
            'is_processed': False,
        })
        response = self.inst.read({})
        self.assertEqual(len(response), 2)

    @parameterized.expand([
        ('ptab_trial_num', 'CTA-101', 1),
        ('trial_filing_date', '2017-05-08', 1),
        ('patent_num', '1111', 1),
    ])
    def test_read_with_params(self, query_field, query_value, expected_length):
        # setup
        self.inst.create({
            'ptab_trial_num': 'CTA-102',
            'trial_filing_date': '2017-05-08',
            'patent_num': '1111',
            'is_cleaned': False,
            'is_processed': False,
        })
        response = self.inst.read({query_field: query_value})
        self.assertEqual(len(response), expected_length)

    def test_read_w_params_ids(self):
        resp = self.inst.read({'ids': []})
        self.assertEqual(0, len(resp))

        resp = self.inst.read({'ids': [self.trial1['id']]})
        self.assertEqual(1, len(resp))
        second_equals_first(
            self.trial1,
            resp[0]
        )

    @parameterized.expand([
        (['9999'], 1),
        (['1111'], 2),
        (['123'], 0),
    ])
    def test_read_with_param_patent_nums(
        self,
        patent_numbers,
        expected_length,
    ):
        # setup
        self.inst.create({
            'ptab_trial_num': 'CTA-102',
            'trial_filing_date': '2017-05-08',
            'patent_num': '1111',
            'is_cleaned': False,
            'is_processed': False,
        })
        self.inst.create({
            'ptab_trial_num': 'CTA-103',
            'trial_filing_date': '2017-05-08',
            'patent_num': '1111',
            'is_cleaned': False,
            'is_processed': False,
        })
        response = self.inst.read({'patent_nums': patent_numbers})
        self.assertEqual(len(response), expected_length)

    def test_update_not_found(self):
        invalid_id = 99999
        args = []
        kwargs = {'id': invalid_id, 'params': {}}
        self.assertRaises(
            TrialNotFoundException,
            self.inst.update,
            *args,
            **kwargs
        )

    def test_update_validation_error_blank_ptab_trial_num(self):
        args = []
        kwargs = {
            'id': self.trial1['id'],
            'params': {
                'ptab_trial_num': '',
            },
        }
        self.assertRaises(
            ValidationError,
            self.inst.update,
            *args,
            **kwargs
        )

    def test_update(self):
        new_data = {'patent_num': '1000'}
        response = self.inst.update(
            id=self.trial1['id'],
            params=new_data,
        )
        second_equals_first(
            new_data,
            response,
        )

    def test_delete_not_found(self):
        invalid_id = 99999
        self.assertRaises(
            TrialNotFoundException,
            self.inst.delete,
            invalid_id,
        )

    def test_delete(self):
        data = self.inst.read({'id': self.trial1['id']})
        self.assertEqual(len(data), 1)
        response = self.inst.delete(id=self.trial1['id'])
        self.assertEqual(response, 'Successfully deleted')
        data = self.inst.read({'id': self.trial1['id']})
        self.assertEqual(len(data), 0)

    def test_upsert_validation_error_missing_ptab_trial_num(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {},
        )

    def test_upsert_create_wo_patent_num(self):
        data = {
            'ptab_trial_num': 'CTA-102',
            'trial_filing_date': '2017-05-06',
        }
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            data,
        )

    def test_upsert(self):
        data = {
            'ptab_trial_num': 'CTA-102',
            'trial_filing_date': '2017-05-06',
            'patent_num': '2222',
            'is_cleaned': False,
            'is_processed': False,
        }
        response = self.inst.upsert(params=data)
        second_equals_first(
            {
                'ptab_trial_num': data['ptab_trial_num'],
                'trial_filing_date': '2017-05-06T00:00:00+00:00',
                'patent_num': data['patent_num'],
            },
            response,
        )

        new_data = {
            'ptab_trial_num': 'CTA-102',
            'trial_filing_date': '2017-05-08',
            'patent_num': '3333',
            'is_cleaned': False,
            'is_processed': False,
        }
        response = self.inst.upsert(params=new_data)
        second_equals_first(
            {
                'ptab_trial_num': new_data['ptab_trial_num'],
                'trial_filing_date': '2017-05-08T00:00:00+00:00',
                'patent_num': new_data['patent_num'],
            },
            response,
        )

    def test_one_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.one,
            {'ptab_trial_num': ''},
        )

    def test_one_raises_multiple_results_found(self):
        # Adding trial with same `patent_num`
        self.inst.create({
            'ptab_trial_num': 'CTA-102',
            'trial_filing_date': '2017-05-06',
            'patent_num': self.trial1['patent_num'],
            'is_cleaned': False,
            'is_processed': False,
        })
        self.assertRaises(
            MultipleResultsFound,
            self.inst.one,
            {'patent_num': self.trial1['patent_num']},
        )

    def test_one_raises_no_result_found(self):
        invalid_patent_num = '1234'
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'patent_num': invalid_patent_num},
        )
