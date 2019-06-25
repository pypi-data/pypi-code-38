from marshmallow import ValidationError
from parameterized import parameterized
from sqlalchemy.exc import IntegrityError

from src.silver_surfer_models.resources.ClaimChallenged import (
    ClaimChallenged,
)
from test.mixins.ClaimDataMixin import ClaimDataMixin
from test.backendtestcase import TestCase
from test.utils import second_equals_first


class ClaimChallengedResourceTestCase(ClaimDataMixin, TestCase):
    def setUp(self):
        super(ClaimChallengedResourceTestCase, self).setUp()

        self.inst = ClaimChallenged()
        self.claim_challenged1 = self.inst.create({
            'ptab2_proceeding_id': self.ptab2_proceeding1['id'],
            'claim_id': self.claim1['id'],
            'prior_art_combination': 0,
            'prior_art_id': self.prior_art1['id'],
            'prior_art_nature': '',
        })
        self.claim_challenged2 = self.inst.create({
            'ptab2_proceeding_id': self.ptab2_proceeding1['id'],
            'claim_id': self.claim2['id'],
            'prior_art_combination': 1,
            'prior_art_id': self.prior_art2['id'],
            'prior_art_nature': 'primary',
        })

    @parameterized.expand([
        'ptab2_proceeding_id',
        'claim_id',
        'prior_art_combination',
        'prior_art_id',
    ])
    def test_create_raises_validation_error(self, missing_field):
        data = {
            'ptab2_proceeding_id': self.ptab2_proceeding1['id'],
            'claim_id': self.claim2['id'],
            'prior_art_combination': 2,
            'prior_art_id': self.prior_art2['id'],
            'prior_art_nature': '',
        }
        data.pop(missing_field)
        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    def test_create_fails_unique_constraint(self):
        self.assertRaises(
            IntegrityError,
            self.inst.create,
            {
                'ptab2_proceeding_id': self.ptab2_proceeding1['id'],
                'claim_id': self.claim1['id'],
                'prior_art_combination': 0,
                'prior_art_id': self.prior_art1['id'],
                'prior_art_nature': '',
            },
        )

    def test_create(self):
        mock_prior_art_combination = 0
        data = {
            'ptab2_proceeding_id': self.ptab2_proceeding1['id'],
            'claim_id': self.claim2['id'],
            'prior_art_combination': mock_prior_art_combination,
            'prior_art_id': self.prior_art1['id'],
            'prior_art_nature': 'primary',
        }
        resp = self.inst.create(data)
        second_equals_first(
            {
                'ptab2_proceeding_id': self.ptab2_proceeding1['id'],
                'claim_id': self.claim2['id'],
                'prior_art_combination': mock_prior_art_combination,
                'prior_art_id': self.prior_art1['id'],
                'prior_art_nature': data['prior_art_nature'],
            },
            resp,
        )

    def test_read_all(self):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

    @parameterized.expand([
        ('ptab2_proceeding_id', 2),
        ('claim_id', 1),
        ('prior_art_id', 1),
        ('prior_art_combination', 1),
        ('prior_art_nature', 1),
    ])
    def test_read_w_params(self, query_field, expected_length):
        resp = self.inst.read({
            query_field: self.claim_challenged1[query_field],
        })
        self.assertEqual(expected_length, len(resp))
        second_equals_first(
            self.claim_challenged1,
            resp[0],
        )

    def test_delete(self):
        response = self.inst.read({'id': self.claim_challenged1['id']})
        self.assertEqual(len(response), 1)
        response = self.inst.delete(id=self.claim_challenged1['id'])
        self.assertEqual(response, 'Successfully deleted')
        response = self.inst.read({'id': self.claim_challenged1['id']})
        self.assertEqual(len(response), 0)

    def test_bulk_delete(self):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))
        self.inst.bulk_delete(ptab2_proceeding_id=self.ptab2_proceeding1['id'])
        resp = self.inst.read({})
        self.assertEqual(0, len(resp))
