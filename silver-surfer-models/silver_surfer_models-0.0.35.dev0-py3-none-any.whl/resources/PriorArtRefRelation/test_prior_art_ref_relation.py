import json
import copy
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.mixins.BasicDataMixin import BasicDataMixin
from test.utils import second_equals_first
from src.silver_surfer_models.resources.CrossRef import CrossRef
from src.silver_surfer_models.resources.PriorArtRefRelation import PriorArtRefRelation


class PriorArtRefRelationResourceTestCase(BasicDataMixin, TestCase):
    def setUp(self):
        super(PriorArtRefRelationResourceTestCase, self).setUp()
        self.inst_cross_ref = CrossRef()
        self.inst = PriorArtRefRelation()

        self.prior_art3 = self.inst_prior_art.create({
            'document_id': self.document2['id'],
            'tag': 'PA 3',
            'title': 'PA3 detail',
            'exhibit': 'EX 300',
        })

        self.prior_art4 = self.inst_prior_art.create({
            'document_id': self.document2['id'],
            'tag': 'PA 4',
            'title': 'PA4 detail',
            'exhibit': 'EX 400',
        })

        self.cross_ref1 = self.inst_cross_ref.create({
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

        self.cross_ref2 = self.inst_cross_ref.create({
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

        self.pa_ref_relation1 = self.inst.create({
            'prior_art_id': self.prior_art1['id'],
            'cross_ref_id': self.cross_ref1['id'],
        })

        self.pa_ref_relation2 = self.inst.create({
            'prior_art_id': self.prior_art1['id'],
            'patent_id': self.patent1['id'],
        })

        self.pa_ref_relation3 = self.inst.create({
            'prior_art_id': self.prior_art1['id'],
            'patent_application_id': self.patent_application1['id'],
        })

        self.valid_data = {
            'prior_art_id': self.prior_art3['id'],
            'cross_ref_id': self.cross_ref1['id'],
            'patent_id': self.patent1['id'],
            'patent_application_id': self.patent_application1['id'],
        }

    def _get_dict_with_fields(self, base_data, fields_to_keep):
        data = {}
        for key in base_data:
            if key in fields_to_keep:
                data[key] = base_data[key]
        return data

    @parameterized.expand([
        (['prior_art_id'],),
        (['cross_ref_id', 'patent_id', 'patent_application_id'],),
    ])
    def test_create_validation_error_missing_field(self, fields_to_keep):
        base_data = copy.copy(self.valid_data)
        data = self._get_dict_with_fields(base_data, fields_to_keep)

        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    def test_create_validation_error_multiple_ref_fields(self):
        data = copy.copy(self.valid_data)
        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        (['prior_art_id', 'cross_ref_id'],),
        (['prior_art_id', 'patent_id'],),
        (['prior_art_id', 'patent_application_id'],),
    ])
    def test_create_violates_unique_constraint(self, fields_to_keep):
        base_data = {
            'prior_art_id': self.prior_art1['id'],
            'cross_ref_id': self.pa_ref_relation1['cross_ref_id'],
            'patent_id': self.pa_ref_relation2['patent_id'],
            'patent_application_id': (
                self.pa_ref_relation3['patent_application_id']),
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)

        self.assertRaises(
            IntegrityError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        ('prior_art_id', ['cross_ref_id']),
        ('cross_ref_id', ['prior_art_id', 'cross_ref_id']),
        ('patent_id', ['prior_art_id', 'patent_id']),
        ('patent_application_id', ['prior_art_id', 'patent_application_id']),
    ])
    def test_create_violates_fk_constraint(
        self,
        field_to_test,
        fields_to_keep,
    ):
        data = self._get_dict_with_fields(self.valid_data, fields_to_keep)
        data[field_to_test] = 999

        self.assertRaises(
            IntegrityError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        (['prior_art_id', 'cross_ref_id'],),
        (['prior_art_id', 'patent_id'],),
        (['prior_art_id', 'patent_application_id'],),
    ])
    def test_create(self, fields_to_keep):
        base_data = copy.copy(self.valid_data)
        data = self._get_dict_with_fields(base_data, fields_to_keep)
        resp = self.inst.create(data)
        second_equals_first(data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

    @parameterized.expand([
        ('id', 'pa_ref_relation1', 'id', 1),
        ('prior_art_id', 'pa_ref_relation1', 'prior_art_id', 3),
        ('cross_ref_id', 'pa_ref_relation1', 'cross_ref_id', 1),
        ('patent_id', 'pa_ref_relation2', 'patent_id', 1),
        (
            'patent_application_id',
            'pa_ref_relation3',
            'patent_application_id',
            1,
        ),
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
            {'prior_art_id': self.prior_art1['id']},
        )

    @parameterized.expand([
        ('id', 'pa_ref_relation1'),
        ('cross_ref_id', 'pa_ref_relation1'),
        ('patent_id', 'pa_ref_relation2'),
        ('patent_application_id', 'pa_ref_relation3'),
    ])
    def test_one(self, field_name, attr):
        pa_ref_relation = getattr(self, attr)
        resp = self.inst.one({
            field_name: pa_ref_relation[field_name],
        })
        second_equals_first(
            pa_ref_relation,
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
        response = self.inst.one({'id': self.pa_ref_relation1['id']})
        self.inst.delete(id=response['id'])
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': self.pa_ref_relation1['id']},
        )
