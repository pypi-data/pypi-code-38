from parameterized import parameterized

from src.silver_surfer_models.resources.ClaimDependency import ClaimDependency
from test.mixins.ClaimDataMixin import ClaimDataMixin
from test.backendtestcase import TestCase
from test.utils import second_equals_first


class ClaimDependencyResourceTestCase(ClaimDataMixin, TestCase):
    def setUp(self):
        super(ClaimDependencyResourceTestCase, self).setUp()

        self.inst = ClaimDependency()
        self.claim_dependency1 = self.inst.create({
            'claim_id': self.claim1['id'],
            'parent_claim_id': self.claim2['id'],
        })
        self.claim_dependency2 = self.inst.create({
            'claim_id': self.claim3['id'],
            'parent_claim_id': self.claim1['id'],
        })
        self.claim_dependency3 = self.inst.create({
            'claim_id': self.claim3['id'],
            'parent_claim_id': self.claim2['id'],
        })

    def test_create(self):
        data = {
            'claim_id': self.claim1['id'],
            'parent_claim_id': self.claim3['id'],
        }
        resp = self.inst.create(data)
        second_equals_first(
            {
                'claim_id': self.claim1['id'],
                'parent_claim_id': self.claim3['id'],
            },
            resp,
        )

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 3)

    @parameterized.expand([
        ('claim_id', 1),
        ('parent_claim_id', 2),
    ])
    def test_read_w_params(self, query_field, expected_length):
        resp = self.inst.read({
            query_field: self.claim_dependency1[query_field],
        })
        self.assertEqual(expected_length, len(resp))

    def test_delete(self):
        response = self.inst.read({'id': self.claim_dependency1['id']})
        self.assertEqual(len(response), 1)
        response = self.inst.delete(id=self.claim_dependency1['id'])
        self.assertEqual(response, 'Successfully deleted')
        response = self.inst.read({'id': self.claim_dependency1['id']})
        self.assertEqual(len(response), 0)
