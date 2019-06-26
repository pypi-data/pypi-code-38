from marshmallow import ValidationError
from parameterized import parameterized

from test.mixins.BasicDataMixin import BasicDataMixin
from src.silver_surfer_models.resources.PriorArt import PriorArt
from test.backendtestcase import TestCase
from test.utils import second_equals_first


class PriorArtResourceTestCase(BasicDataMixin, TestCase):
    def setUp(self):
        super(PriorArtResourceTestCase, self).setUp()
        self.inst = PriorArt()

    def test_create(self):
        data = {
            'ptab2_document_id': self.ptab2_document1['id'],
            'tag': 'Jackson',
            'title': 'U.S 1234',
            'exhibit': 'EX 1010',
        }
        resp = self.inst.create(data)
        second_equals_first(
            data,
            resp,
        )

    def test_create_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {},
        )

    def test_create_validation_error_blank_tag(self):
        data = {
            'ptab2_document_id': self.ptab2_document1['id'],
            'tag': '',
            'title': 'U.S 1234',
            'exhibit': 'EX 1010',
        }
        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

    @parameterized.expand([
        ('ptab2_document_id', 'prior_art1', 'ptab2_document_id', 'prior_art1'),
        ('tag', 'prior_art2', 'tag', 'prior_art2'),
    ])
    def test_read_w_params(
        self,
        query_field,
        attr1,
        attr2,
        expected_prior_art_attr,
    ):
        resp = self.inst.read({
            query_field: getattr(self, attr1)[attr2],
        })
        self.assertEqual(1, len(resp))
        expected_prior_art = getattr(self, expected_prior_art_attr)
        self.assertEqual(
            expected_prior_art['id'],
            resp[0]['id'],
        )

    def test_update(self):
        new_data = {
            'ptab2_document_id': 9999,
            'tag': 'what what',
            'title': 'some some',
        }
        resp = self.inst.update(
            id=self.prior_art1['id'],
            params=new_data,
        )
        second_equals_first(
            {
                'id': self.prior_art1['id'],
                'ptab2_document_id': self.prior_art1['ptab2_document_id'],
                'tag': self.prior_art1['tag'],
                'title': new_data['title'],
            },
            resp,
        )

    def test_delete(self):
        response = self.inst.read({'id': self.prior_art1['id']})
        self.assertEqual(len(response), 1)
        response = self.inst.delete(id=self.prior_art1['id'])
        self.assertEqual(response, 'Successfully deleted')
        response = self.inst.read({'id': self.prior_art1['id']})
        self.assertEqual(len(response), 0)

    def test_upsert_raises_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {},
        )

    def test_upsert_creates_a_new_prior_art(self):
        self.assertEqual(2, len(self.inst.read({})))
        data = {
            'ptab2_document_id': self.ptab2_document1['id'],
            'tag': 'Jackson',
            'title': 'U.S 1234',
            'exhibit': '',
        }
        resp = self.inst.upsert(data)
        second_equals_first(
            data,
            resp,
        )
        self.assertEqual(3, len(self.inst.read({})))

    def test_upsert_updates_existing(self):
        self.assertEqual(2, len(self.inst.read({})))
        data = {
            'ptab2_document_id': self.prior_art1['ptab2_document_id'],
            'tag': self.prior_art1['tag'],
            'title': 'Something new',
            'exhibit': 'EX 2123',
        }
        resp = self.inst.upsert(data)
        second_equals_first(
            data,
            resp,
        )
        self.assertEqual(2, len(self.inst.read({})))
