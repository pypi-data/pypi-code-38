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
from src.silver_surfer_models.resources.PTAB2Decision import PTAB2Decision


class PTAB2DecisionResourceTestCase(TestCase):
    def setUp(self):
        super(PTAB2DecisionResourceTestCase, self).setUp()
        self.inst = PTAB2Decision()

        self.ptab2_decision1 = self.inst.create({
            'board_rulings': json.dumps([
                '35 USC 311',
                '35 USC 312',
                '35 USC 318',
                '37 CFR 42.73',
                '37 CFR 42.100'
            ]),
            'decision_date': '05-02-2019',
            'decision_type_category': 'Decision',
            'document_identifier': '169812221',
            'document_name': 'IPR2018-00107 Final Written Decision.pdf',
            'identifier': '1000',
            'issue_type': json.dumps(['102', '103']),
            'petitioner_application_number_text': '-',
            'petitioner_counsel_name': 'Tedd Van Buskirk',
            'petitioner_grant_date': '-',
            'petitioner_group_art_unit_number': '-',
            'petitioner_inventor_name': '-',
            'petitioner_party_name': 'St. Jude Medical, LLC',
            'petitioner_patent_number': '-',
            'petitioner_patent_owner_name': '-',
            'petitioner_technology_center_number': '-',
            'proceeding_number': 'IPR2018-001',
            'proceeding_type_category': 'AIA Trial',
            'respondent_application_number_text': '10135746',
            'respondent_counsel_name': 'Matthew Antonelli',
            'respondent_grant_date': '11-23-2004',
            'respondent_group_art_unit_number': '3738',
            'respondent_inventor_name': '-',
            'respondent_party_name': 'Snyders Heart Valve LLC',
            'respondent_patent_number': '6821297',
            'respondent_patent_owner_name': 'Snyders, Robert V.',
            'respondent_technology_center_number': '3700',
            'subdecision_type_category': 'Final Decision',
            'subproceeding_type_category': 'IPR',
        })

        self.ptab2_decision2 = self.inst.create({
            'board_rulings': json.dumps([
                '35 USC 311',
                '35 USC 312',
                '35 USC 318',
                '37 CFR 42.73',
                '37 CFR 42.100'
            ]),
            'decision_date': '05-02-2019',
            'decision_type_category': 'Decision',
            'document_identifier': '169812221',
            'document_name': 'IPR2018-00107 Final Written Decision.pdf',
            'identifier': '2000',
            'issue_type': json.dumps(['102', '103']),
            'petitioner_application_number_text': '-',
            'petitioner_counsel_name': 'Tedd Van Buskirk',
            'petitioner_grant_date': '-',
            'petitioner_group_art_unit_number': '-',
            'petitioner_inventor_name': '-',
            'petitioner_party_name': 'St. Jude Medical, LLC',
            'petitioner_patent_number': '-',
            'petitioner_patent_owner_name': '-',
            'petitioner_technology_center_number': '-',
            'proceeding_number': 'IPR2018-002',
            'proceeding_type_category': 'AIA Trial',
            'respondent_application_number_text': '10135746',
            'respondent_counsel_name': 'Matthew Antonelli',
            'respondent_grant_date': '11-23-2004',
            'respondent_group_art_unit_number': '3738',
            'respondent_inventor_name': '-',
            'respondent_party_name': 'Snyders Heart Valve LLC',
            'respondent_patent_number': '6821297',
            'respondent_patent_owner_name': 'Snyders, Robert V.',
            'respondent_technology_center_number': '3700',
            'subdecision_type_category': 'Final Decision',
            'subproceeding_type_category': 'IPR',
        })

        self.valid_data = {
            'board_rulings': json.dumps([
                '35 USC 311',
                '35 USC 312',
                '35 USC 318',
                '37 CFR 42.73',
                '37 CFR 42.100'
            ]),
            'decision_date': '05-02-2019',
            'decision_type_category': 'Decision',
            'document_identifier': '169812221',
            'document_name': 'IPR2018-00107 Final Written Decision.pdf',
            'identifier': '3000',
            'issue_type': json.dumps(['102', '103']),
            'petitioner_application_number_text': '-',
            'petitioner_counsel_name': 'Tedd Van Buskirk',
            'petitioner_grant_date': '-',
            'petitioner_group_art_unit_number': '-',
            'petitioner_inventor_name': '-',
            'petitioner_party_name': 'St. Jude Medical, LLC',
            'petitioner_patent_number': '-',
            'petitioner_patent_owner_name': '-',
            'petitioner_technology_center_number': '-',
            'proceeding_number': 'IPR2018-007',
            'proceeding_type_category': 'AIA Trial',
            'respondent_application_number_text': '10135746',
            'respondent_counsel_name': 'Matthew Antonelli',
            'respondent_grant_date': '11-23-2004',
            'respondent_group_art_unit_number': '3738',
            'respondent_inventor_name': '-',
            'respondent_party_name': 'Snyders Heart Valve LLC',
            'respondent_patent_number': '6821297',
            'respondent_patent_owner_name': 'Snyders, Robert V.',
            'respondent_technology_center_number': '3700',
            'subdecision_type_category': 'Final Decision',
            'subproceeding_type_category': 'IPR',
        }

    def test_create_violates_unique_constraint(self):
        data = copy.copy(self.valid_data)
        data['identifier'] = self.ptab2_decision1['identifier']
        self.assertRaises(
            IntegrityError,
            self.inst.create,
            data,
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        expected_data = {
            **self.valid_data,
            **{
                'decision_date': '2019-05-02T00:00:00+00:00',
                'respondent_grant_date': '2004-11-23T00:00:00+00:00',
            }
        }
        second_equals_first(expected_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

    @parameterized.expand([
        ('id', 'ptab2_decision1', 'id', 1),
        ('identifier', 'ptab2_decision1', 'identifier', 1),
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
        ('identifier',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.ptab2_decision1[field_name],
        })
        second_equals_first(
            self.ptab2_decision1,
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
        response = self.inst.one({'id': self.ptab2_decision1['id']})
        self.inst.delete(id=response['id'])
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': self.ptab2_decision1['id']},
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'decision_date': self.valid_data['decision_date'],
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
            **{'identifier': self.ptab2_decision1['identifier']},
        }
        resp = self.inst.upsert(data)
        expected_data = {
            **data,
            **{
                'decision_date': '2019-05-02T00:00:00+00:00',
                'respondent_grant_date': '2004-11-23T00:00:00+00:00',
            }
        }
        second_equals_first(
            expected_data,
            resp,
        )
        self.assertEqual(2, len(self.inst.read({})))
