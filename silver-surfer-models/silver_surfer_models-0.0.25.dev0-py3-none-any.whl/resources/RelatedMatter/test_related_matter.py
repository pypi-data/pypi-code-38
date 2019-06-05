from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.Trial import Trial
from src.silver_surfer_models.resources.Document import Document
from src.silver_surfer_models.resources.PacerCase import PacerCase
from src.silver_surfer_models.resources.RelatedMatter import RelatedMatter
from src.silver_surfer_models.resources.Document.document_types import DOCUMENT_TYPES


class RelatedMatterResourceTestCase(TestCase):
    def setUp(self):
        super(RelatedMatterResourceTestCase, self).setUp()
        self.inst_trial = Trial()
        self.inst_document = Document()
        self.inst_pacer_case = PacerCase()
        self.inst = RelatedMatter()

        self.trial1 = self.inst_trial.create({
            'ptab_trial_num': 'CTA-101',
            'trial_filing_date': '2017-05-06',
            'patent_num': '9999',
            'is_cleaned': False,
            'is_processed': False,
        })
        self.trial2 = self.inst_trial.create({
            'ptab_trial_num': 'CTA-201',
            'trial_filing_date': '2017-05-06',
            'patent_num': '9999',
            'is_cleaned': False,
            'is_processed': False,
        })
        self.trial3 = self.inst_trial.create({
            'ptab_trial_num': 'CTA-301',
            'trial_filing_date': '2017-05-06',
            'patent_num': '9999',
            'is_cleaned': False,
            'is_processed': False,
        })
        self.document1 = self.inst_document.create({
            'trial_id': self.trial1['id'],
            'ptab_document_id': 2222,
            'type': DOCUMENT_TYPES['petition'],
            'has_smart_doc': True,
        })
        self.pacer_case1 = self.inst_pacer_case.create({
            'case_no': '3:17-cv-05314-SDW-LDW',
            'court_id': 'njd',
            'pacer_case_external_id': '2000',
            'cause': '15:1126 Patent Infringement',
        })
        self.pacer_case2 = self.inst_pacer_case.create({
            'case_no': '4:17-cv-05314-SDW-LDW',
            'court_id': 'njd',
            'pacer_case_external_id': '3000',
            'cause': '15:1126 Patent Infringement',
        })
        self.pacer_case3 = self.inst_pacer_case.create({
            'case_no': '5:17-cv-05314-SDW-LDW',
            'court_id': 'njd',
            'pacer_case_external_id': '4000',
            'cause': '15:1126 Patent Infringement',
        })

        self.related_matter1 = self.inst.create({
            'document_id': self.document1['id'],
            'pacer_case_id': self.pacer_case1['id'],
        })

        self.related_matter2 = self.inst.create({
            'document_id': self.document1['id'],
            'pacer_case_id': self.pacer_case2['id'],
        })

        self.related_matter3 = self.inst.create({
            'document_id': self.document1['id'],
            'trial_id': self.trial2['id'],
        })

    def _get_dict_with_fields(self, base_data, fields_to_keep):
        data = {}
        for key in base_data:
            if key in fields_to_keep:
                data[key] = base_data[key]
        return data

    @parameterized.expand([
        (['document_id'],),
        (['pacer_case_id', 'trial_id'],),
    ])
    def test_create_validation_error_missing_field(self, fields_to_keep):
        base_data = {
            'document_id': self.document1['id'],
            'pacer_case_id': self.pacer_case3['id'],
            'trial_id': self.trial3['id'],
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)

        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    def test_create_validation_error_both_fields(self):
        data = {
            'document_id': self.document1['id'],
            'pacer_case_id': self.pacer_case3['id'],
            'trial_id': self.trial3['id'],
        }
        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        (['document_id', 'pacer_case_id'],),
        (['document_id', 'trial_id'],),
    ])
    def test_create_violates_unique_constraint(self, fields_to_keep):
        base_data = {
            'document_id': self.document1['id'],
            'pacer_case_id': self.pacer_case2['id'],
            'trial_id': self.trial2['id'],
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)

        self.assertRaises(
            IntegrityError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        ('document_id', ['pacer_case_id']),
        ('pacer_case_id', ['document_id', 'pacer_case_id']),
        ('trial_id', ['document_id', 'trial_id']),
    ])
    def test_create_violates_fk_constraint(
        self,
        field_to_test,
        fields_to_keep,
    ):
        base_data = {
            'document_id': self.document1['id'],
            'pacer_case_id': self.pacer_case2['id'],
            'trial_id': self.trial2['id'],
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)
        data[field_to_test] = 999

        self.assertRaises(
            IntegrityError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        (['document_id', 'pacer_case_id'],),
        (['document_id', 'trial_id'],),
    ])
    def test_create(self, fields_to_keep):
        base_data = {
            'document_id': self.document1['id'],
            'pacer_case_id': self.pacer_case3['id'],
            'trial_id': self.trial3['id'],
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)
        resp = self.inst.create(data)
        second_equals_first(data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

    @parameterized.expand([
        ('id', 'related_matter1', 'id', 1),
        ('document_id', 'document1', 'id', 3),
        ('pacer_case_id', 'pacer_case1', 'id', 1),
        ('trial_id', 'trial2', 'id', 1),
    ])
    def test_read_w_params(
        self,
        field_name,
        attr,
        attr_field,
        expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 3)

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
            {'document_id': self.document1['id']},
        )

    @parameterized.expand([
        ('id', 'related_matter1'),
        ('pacer_case_id', 'related_matter1'),
        ('trial_id', 'related_matter3'),
    ])
    def test_one(self, field_name, attr):
        related_matter = getattr(self, attr)
        resp = self.inst.one({
            field_name: related_matter[field_name],
        })
        second_equals_first(
            related_matter,
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
        response = self.inst.one({'id': self.related_matter1['id']})
        self.inst.delete(id=response['id'])
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': self.related_matter1['id']},
        )
