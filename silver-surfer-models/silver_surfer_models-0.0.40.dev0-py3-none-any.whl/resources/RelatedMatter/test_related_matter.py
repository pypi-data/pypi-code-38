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
from src.silver_surfer_models.resources.PacerCase import PacerCase
from src.silver_surfer_models.resources.RelatedMatter import RelatedMatter


class RelatedMatterResourceTestCase(BasicDataMixin, TestCase):
    def setUp(self):
        super(RelatedMatterResourceTestCase, self).setUp()
        self.inst_pacer_case = PacerCase()
        self.inst = RelatedMatter()

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

        self.ptab2_proceeding3 = self.inst_ptab2_proceeding.create({
            'accorded_filing_date': '05-06-2013',
            'decision_date': '10-07-2014',
            'institution_decision_date': '10-08-2013',
            'petitioner_application_number_text': '-',
            'petitioner_counsel_name': 'Steven Baughman',
            'petitioner_grant_date': '-',
            'petitioner_group_art_unit_number': '-',
            'petitioner_inventor_name': '-',
            'petitioner_party_name': 'Apple Inc.',
            'petitioner_patent_number': '-',
            'petitioner_patent_owner_name': '-',
            'petitioner_technology_center_number': '-',
            'proceeding_filing_date': '05-06-2013',
            'proceeding_last_modified_date': '-',
            'proceeding_number': 'IPR-30033',
            'proceeding_status_category': 'FWD Entered',
            'proceeding_type_category': 'AIA Trial',
            'respondent_application_number_text': '08471964',
            'respondent_counsel_name': 'David Marsh',
            'respondent_grant_date': '10-12-1999',
            'respondent_group_art_unit_number': '-',
            'respondent_inventor_name': 'ARTHUR HAIR',
            'respondent_party_name': 'SightSound Technologies LLC',
            'respondent_patent_number': '5966440',
            'respondent_patent_owner_name': 'SightSound Technologies LLC',
            'respondent_technology_center_number': '2100',
            'subproceeding_type_category': 'CBM',
            'proceeding_status': None,
        })

        self.related_matter1 = self.inst.create({
            'ptab2_document_id': self.ptab2_document1['id'],
            'related_pacer_case_id': self.pacer_case1['id'],
        })

        self.related_matter2 = self.inst.create({
            'ptab2_document_id': self.ptab2_document1['id'],
            'related_pacer_case_id': self.pacer_case2['id'],
        })

        self.related_matter3 = self.inst.create({
            'ptab2_document_id': self.ptab2_document1['id'],
            'related_ptab2_proceeding_id': self.ptab2_proceeding2['id'],
        })

    def _get_dict_with_fields(self, base_data, fields_to_keep):
        data = {}
        for key in base_data:
            if key in fields_to_keep:
                data[key] = base_data[key]
        return data

    @parameterized.expand([
        (['ptab2_document_id'],),
        (['related_pacer_case_id', 'related_ptab2_proceeding_id'],),
    ])
    def test_create_validation_error_missing_field(self, fields_to_keep):
        base_data = {
            'ptab2_document_id': self.ptab2_document1['id'],
            'related_pacer_case_id': self.pacer_case3['id'],
            'related_ptab2_proceeding_id': self.ptab2_proceeding3['id'],
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)

        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    def test_create_validation_error_both_fields(self):
        data = {
            'ptab2_document_id': self.ptab2_document1['id'],
            'related_pacer_case_id': self.pacer_case3['id'],
            'related_ptab2_proceeding_id': self.ptab2_proceeding3['id'],
        }
        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        (['ptab2_document_id', 'related_pacer_case_id'],),
        (['ptab2_document_id', 'related_ptab2_proceeding_id'],),
    ])
    def test_create_violates_unique_constraint(self, fields_to_keep):
        base_data = {
            'ptab2_document_id': self.ptab2_document1['id'],
            'related_pacer_case_id': self.pacer_case2['id'],
            'related_ptab2_proceeding_id': self.ptab2_proceeding2['id'],
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)

        self.assertRaises(
            IntegrityError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        ('ptab2_document_id', ['related_pacer_case_id']),
        ('related_pacer_case_id', ['ptab2_document_id', 'related_pacer_case_id']),
        ('related_ptab2_proceeding_id', ['ptab2_document_id', 'related_ptab2_proceeding_id']),
    ])
    def test_create_violates_fk_constraint(
        self,
        field_to_test,
        fields_to_keep,
    ):
        base_data = {
            'ptab2_document_id': self.ptab2_document1['id'],
            'related_pacer_case_id': self.pacer_case2['id'],
            'related_ptab2_proceeding_id': self.ptab2_proceeding2['id'],
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)
        data[field_to_test] = 999

        self.assertRaises(
            IntegrityError,
            self.inst.create,
            data,
        )

    @parameterized.expand([
        (['ptab2_document_id', 'related_pacer_case_id'],),
        (['ptab2_document_id', 'related_ptab2_proceeding_id'],),
    ])
    def test_create(self, fields_to_keep):
        base_data = {
            'ptab2_document_id': self.ptab2_document1['id'],
            'related_pacer_case_id': self.pacer_case3['id'],
            'related_ptab2_proceeding_id': self.ptab2_proceeding3['id'],
        }
        data = self._get_dict_with_fields(base_data, fields_to_keep)
        resp = self.inst.create(data)
        second_equals_first(data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

    @parameterized.expand([
        ('id', 'related_matter1', 'id', 1),
        ('ptab2_document_id', 'ptab2_document1', 'id', 3),
        ('related_pacer_case_id', 'pacer_case1', 'id', 1),
        ('related_ptab2_proceeding_id', 'ptab2_proceeding2', 'id', 1),
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
            {'ptab2_document_id': self.ptab2_document1['id']},
        )

    @parameterized.expand([
        ('id', 'related_matter1'),
        ('related_pacer_case_id', 'related_matter1'),
        ('related_ptab2_proceeding_id', 'related_matter3'),
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
