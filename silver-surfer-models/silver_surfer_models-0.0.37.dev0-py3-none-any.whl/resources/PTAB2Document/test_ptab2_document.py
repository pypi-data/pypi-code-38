import copy
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.File import File
from src.silver_surfer_models.resources.PTAB2Document import PTAB2Document


class PTAB2DocumentResourceTestCase(TestCase):
    def setUp(self):
        super(PTAB2DocumentResourceTestCase, self).setUp()
        self.inst = PTAB2Document()
        self.inst_file = File()

        self.file1 = self.inst_file.create({
            'file_format': 'pdf',
            's3_bucket_name': 'test-bucket',
            's3_key_name': 'key1123',
        })

        self.ptab2_document1 = self.inst.create({
            'document_category': 'Exhibits',
            'document_filing_date': '05-08-2019',
            'document_identifier': '1000',
            'document_name': 'Exhibit 1066 - EC-Naprosyn 2004 label.pdf',
            'document_number': '1066',
            'document_size': '-',
            'document_title_text': 'EC Naprosyn 2004 label',
            'document_type_name': 'EXHIBIT',
            'filing_party_category': '-',
            'media_type_category': '-',
            'petitioner_application_number_text': '-',
            'petitioner_counsel_name': 'Alan H. Pollack',
            'petitioner_grant_date': '-',
            'petitioner_group_art_unit_number': '-',
            'petitioner_inventor_name': '-',
            'petitioner_party_name': 'Mylan Pharmaceuticals Inc.',
            'petitioner_patent_number': '-',
            'petitioner_patent_owner_name': '-',
            'petitioner_technology_center_number': '-',
            'proceeding_number': 'IPR2018-00272',
            'proceeding_type_category': 'AIA Trial',
            'respondent_application_number_text': '14980639',
            'respondent_counsel_name': 'Thomas Blinka',
            'respondent_grant_date': '07-19-2016',
            'respondent_group_art_unit_number': '1617',
            'respondent_inventor_name': '-',
            'respondent_party_name': 'Horizon Pharma USA, Inc.',
            'respondent_patent_number': '9393208',
            'respondent_patent_owner_name': 'AULT et al',
            'respondent_technology_center_number': '1600',
            'subproceeding_type_category': 'IPR',
        })

        self.ptab2_document2 = self.inst.create({
            'document_category': 'Exhibits',
            'document_filing_date': '05-08-2019',
            'document_identifier': '2000',
            'document_name': 'Exhibit 1066 - EC-Naprosyn 2004 label.pdf',
            'document_number': '1066',
            'document_size': '-',
            'document_title_text': 'EC Naprosyn 2004 label',
            'document_type_name': 'EXHIBIT',
            'filing_party_category': '-',
            'media_type_category': '-',
            'petitioner_application_number_text': '-',
            'petitioner_counsel_name': 'Alan H. Pollack',
            'petitioner_grant_date': '-',
            'petitioner_group_art_unit_number': '-',
            'petitioner_inventor_name': '-',
            'petitioner_party_name': 'Mylan Pharmaceuticals Inc.',
            'petitioner_patent_number': '-',
            'petitioner_patent_owner_name': '-',
            'petitioner_technology_center_number': '-',
            'proceeding_number': 'IPR2018-00272',
            'proceeding_type_category': 'AIA Trial',
            'respondent_application_number_text': '14980639',
            'respondent_counsel_name': 'Thomas Blinka',
            'respondent_grant_date': '07-19-2016',
            'respondent_group_art_unit_number': '1617',
            'respondent_inventor_name': '-',
            'respondent_party_name': 'Horizon Pharma USA, Inc.',
            'respondent_patent_number': '9393208',
            'respondent_patent_owner_name': 'AULT et al',
            'respondent_technology_center_number': '1600',
            'subproceeding_type_category': 'IPR',
            'has_smart_doc': True,
        })

        self.valid_data = {
            'document_category': 'Exhibits',
            'document_filing_date': '05-08-2019',
            'document_identifier': '3000',
            'document_name': 'Exhibit 1066 - EC-Naprosyn 2004 label.pdf',
            'document_number': '1066',
            'document_size': '-',
            'document_title_text': 'EC Naprosyn 2004 label',
            'document_type_name': 'EXHIBIT',
            'filing_party_category': '-',
            'media_type_category': '-',
            'petitioner_application_number_text': '-',
            'petitioner_counsel_name': 'Alan H. Pollack',
            'petitioner_grant_date': '-',
            'petitioner_group_art_unit_number': '-',
            'petitioner_inventor_name': '-',
            'petitioner_party_name': 'Mylan Pharmaceuticals Inc.',
            'petitioner_patent_number': '-',
            'petitioner_patent_owner_name': '-',
            'petitioner_technology_center_number': '-',
            'proceeding_number': 'IPR2018-00272',
            'proceeding_type_category': 'AIA Trial',
            'respondent_application_number_text': '14980639',
            'respondent_counsel_name': 'Thomas Blinka',
            'respondent_grant_date': '07-19-2016',
            'respondent_group_art_unit_number': '1617',
            'respondent_inventor_name': '-',
            'respondent_party_name': 'Horizon Pharma USA, Inc.',
            'respondent_patent_number': '9393208',
            'respondent_patent_owner_name': 'AULT et al',
            'respondent_technology_center_number': '1600',
            'subproceeding_type_category': 'IPR',
            'file_id': self.file1['id'],
        }

    def test_create_violates_unique_constraint(self):
        data = copy.copy(self.valid_data)
        data['document_identifier'] = (
            self.ptab2_document1['document_identifier'])
        self.assertRaises(
            IntegrityError,
            self.inst.create,
            data,
        )

    def test_create_violates_fk_constraint(self):
        data = copy.copy(self.valid_data)
        file_id_that_dne = 91923891283
        data['file_id'] = file_id_that_dne
        self.assertRaises(
            Exception,
            self.inst.create,
            data,
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        expected_data = {
            **self.valid_data,
            **{
                'document_filing_date': '2019-05-08T00:00:00+00:00',
                'petitioner_grant_date': None,
                'respondent_grant_date': '2016-07-19T00:00:00+00:00',
            }
        }
        second_equals_first(expected_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

    @parameterized.expand([
        ('id', 'ptab2_document1', 'id', 1),
        ('document_identifier', 'ptab2_document1', 'document_identifier', 1),
        ('proceeding_number', 'ptab2_document1', 'proceeding_number', 2),
        ('has_smart_doc', 'ptab2_document2', 'has_smart_doc', 1),
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
        ('document_identifier',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.ptab2_document1[field_name],
        })
        second_equals_first(
            self.ptab2_document1,
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
        response = self.inst.one({'id': self.ptab2_document1['id']})
        self.inst.delete(id=response['id'])
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': self.ptab2_document1['id']},
        )

    def test_update_violates_fk_constraint(self):
        invalid_file_id = 123345
        self.assertRaises(
            IntegrityError,
            self.inst.update,
            self.ptab2_document1['id'],
            {'file_id': invalid_file_id},
        )

    def test_update_raises_validation_error(self):
        invalid_file_id = 'asd'
        self.assertRaises(
            ValidationError,
            self.inst.update,
            self.ptab2_document1['id'],
            {'file_id': invalid_file_id},
        )

    def test_partial_update_file_id(self):
        self.assertIsNone(self.ptab2_document1['file_id'])

        self.inst.update(
            self.ptab2_document1['id'],
            {'file_id': self.file1['id']},
        )

        response = self.inst.one({'id': self.ptab2_document1['id']})
        self.assertEqual(self.file1['id'], response['file_id'])

    def test_partial_update_has_smart_doc(self):
        self.assertFalse(self.ptab2_document1['has_smart_doc'])

        self.inst.update(
            self.ptab2_document1['id'],
            {'has_smart_doc': True},
        )

        response = self.inst.one({'id': self.ptab2_document1['id']})
        self.assertTrue(response['has_smart_doc'])

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'petitioner_party_name': (
                    self.valid_data['petitioner_party_name']),
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
            **{'document_identifier': (
                self.ptab2_document1['document_identifier'])},
        }
        resp = self.inst.upsert(data)
        expected_data = {
            **data,
            **{
                'document_filing_date': '2019-05-08T00:00:00+00:00',
                'petitioner_grant_date': None,
                'respondent_grant_date': '2016-07-19T00:00:00+00:00',
            }
        }
        second_equals_first(
            expected_data,
            resp,
        )
        self.assertEqual(2, len(self.inst.read({})))

    def test_bulk_create(self):
        mock_document1 = {
            **self.valid_data,
            **{'document_identifier': '1'},
        }
        mock_document2 = {
            **self.valid_data,
            **{'document_identifier': '2'},
        }
        mappings = [
            mock_document1,
            mock_document2,
        ]
        response = self.inst.read({})
        self.assertEqual(2, len(response))

        self.inst.bulk_create(mappings)
        response = self.inst.read({})
        self.assertEqual(4, len(response))
