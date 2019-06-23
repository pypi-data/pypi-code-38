import json
import copy
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.CrossRef import CrossRef


class CrossRefResourceTestCase(TestCase):
    def setUp(self):
        super(CrossRefResourceTestCase, self).setUp()
        self.inst = CrossRef()

        self.cross_ref1 = self.inst.create({
            'doi': '1000',
            'authors': json.dumps([
                {'family': 'Flechter', 'given': 'Shlomo'},
                {'family': 'Kott', 'given': 'Edna'},
            ]),
            'doi_url': 'http://dx.doi.org/10.1097/00002826-200201000-00002',
            'issn': json.dumps(['0362-5664']),
            'issue': '1',
            'journal': 'Clinical neuropharmacology',
            'pages': '11-5',
            'pmid': '11852290',
            'ref_type': 'journal-article',
            'text': 'Shlomo Flechter et al., Copolymer 1'
                    'Relapsing Forms of Multiple Sclerosis: Open '
                    'Multicenter Study of Alternate-Day Administration.',
            'title': 'Copolymer 1 (glatiramer acetate) in relapsing forms ',
            'volume': '25',
            'year': 2002,
        })

        self.cross_ref2 = self.inst.create({
            'doi': '2000',
            'authors': json.dumps([
                {'family': 'Flechter', 'given': 'Shlomo'},
            ]),
            'doi_url': 'http://dx.doi.org/10.1097/00002826-200201000-00002',
            'issn': json.dumps(['0362-5664']),
            'issue': '1123',
            'journal': 'Clinical neuropharmacology',
            'pages': '11-5',
            'pmid': '11852290',
            'ref_type': 'journal-article',
            'text': 'Shlomo Flechter et al., Copolymer 1'
                    'Relapsing Forms of Multiple Sclerosis: Open Multicenter '
                    'Study of Alternate-Day Administration.',
            'title': 'Copolymer 1 (glatiramer acetate) in relapsing forms ',
            'volume': '25',
            'year': 2002,
        })

        self.valid_data = {
            'doi': '3000',
            'authors': json.dumps([
                {'family': 'Flechter', 'given': 'Shlomo'},
            ]),
            'doi_url': 'http://dx.doi.org/10.1097/00002826-200201000-00002',
            'issn': json.dumps(['0362-5664']),
            'issue': '1123',
            'journal': 'Clinical neuropharmacology',
            'pages': '11-5',
            'pmid': '11852290',
            'ref_type': 'journal-article',
            'text': 'Shlomo Flechter et al., Copolymer 1'
            'Relapsing Forms of Multiple Sclerosis: Open Multicenter Study of '
            'Alternate-Day Administration.',
            'title': 'Copolymer 1 (glatiramer acetate) in relapsing forms ',
            'volume': '25',
            'year': 2002,
        }

    @parameterized.expand([
        ('doi',),
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
            {'doi': self.cross_ref1['doi']},
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        second_equals_first(self.valid_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

    @parameterized.expand([
        ('id', 'cross_ref1', 'id', 1),
        ('doi', 'cross_ref1', 'doi', 1),
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
        ('doi',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.cross_ref1[field_name],
        })
        second_equals_first(
            self.cross_ref1,
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
        response = self.inst.one({'id': self.cross_ref1['id']})
        self.inst.delete(id=response['id'])
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': self.cross_ref1['id']},
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'doi_url': self.valid_data['doi_url'],
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
            **{'doi': self.cross_ref1['doi']},
        }
        resp = self.inst.upsert(data)
        second_equals_first(
            data,
            resp,
        )
        self.assertEqual(2, len(self.inst.read({})))
