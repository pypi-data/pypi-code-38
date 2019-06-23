from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.Document import (
    Document,
)
from src.silver_surfer_models.resources.File import File
from src.silver_surfer_models.resources.Trial import Trial
from src.silver_surfer_models.resources.Document.document_types import (
    DOCUMENT_TYPES,
)


class DocumentResourceTestCase(TestCase):
    def setUp(self):
        super(DocumentResourceTestCase, self).setUp()
        self.inst = Document()
        self.inst_file = File()
        self.inst_trial = Trial()

        self.trial1 = self.inst_trial.create({
            'ptab_trial_num': 'CTA-101',
            'trial_filing_date': '2017-05-06',
            'patent_num': '9999',
            'is_cleaned': False,
            'is_processed': False,
        })
        self.trial2 = self.inst_trial.create({
            'ptab_trial_num': 'CTA-102',
            'trial_filing_date': '2017-05-06',
            'patent_num': '1000',
            'is_cleaned': False,
            'is_processed': False,
        })
        self.file1 = self.inst_file.create({
            'file_format': 'pdf',
            's3_bucket_name': 'test-bucket',
            's3_key_name': 'key1123',
        })

        self.document1 = self.inst.create({
            'trial_id': self.trial1['id'],
            'ptab_document_id': 1111,
            'file_id': self.file1['id'],
            'type': DOCUMENT_TYPES['petition'],
            'title': 'Inter Partes Review Petition of US 7879828',
            'document_number': '2002',
        })
        self.document2 = self.inst.create({
            'trial_id': self.trial2['id'],
            'ptab_document_id': 2222,
            'type': DOCUMENT_TYPES['final'],
            'has_smart_doc': True,
        })
        self.document3 = self.inst.create({
            'trial_id': self.trial1['id'],
            'ptab_document_id': 3333,
            'type': DOCUMENT_TYPES['petition'],
            'title': 'Inter Partes Review Petition',
            'is_petition_doc': True,
        })

    def test_create_validation_error_no_trial_id(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {
                'ptab_document_id': 1111,
                'title': 'Doc 1',
                'filing_date': '2017-07-05',
                'type': 'original_final',
            }
        )

    def test_create_validation_error_no_ptab_document_id(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {
                'trial_id': self.trial1['id'],
                'title': 'Doc 1',
                'filing_date': '2017-07-05',
                'type': 'original_final',
            }
        )

    def test_create_fails_for_duplicate_ptab_document_id(self):
        self.assertRaises(
            IntegrityError,
            self.inst.create,
            {
                'trial_id': self.trial1['id'],
                'ptab_document_id': self.document1['ptab_document_id'],
                'title': 'Doc2',
                'filing_date': '2017-07-05',
                'type': DOCUMENT_TYPES['final'],
            }
        )

    def test_create(self):
        data = {
            'trial_id': self.trial1['id'],
            'ptab_document_id': 4444,
            'title': 'Doc2',
            'filing_date': '2017-07-05',
            'type': DOCUMENT_TYPES['final'],
            'exhibit_number': '10001',
        }
        resp = self.inst.create(data)
        second_equals_first(
            {
                'trial_id': self.trial1['id'],
                'ptab_document_id': data['ptab_document_id'],
                'title': data['title'],
                'filing_date': '2017-07-05T00:00:00+00:00',
                'type': data['type'],
                'file_id': None,
            },
            resp,
        )

    def test_read_all(self):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

    @parameterized.expand([
        ('trial_id', 'trial1', 'id', 2),
        ('ptab_document_id', 'document1', 'ptab_document_id', 1),
        ('file_id', 'file1', 'id', 1),
    ])
    def test_read_w_params1(
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

    @parameterized.expand([
        ('type', DOCUMENT_TYPES['final'], 1),
        ('has_smart_doc', True, 1),
        ('file_id', None, 2),
    ])
    def test_read_w_params2(self, field_name, field_value, expected_length):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

        resp = self.inst.read({
            field_name: field_value,
        })
        self.assertEqual(expected_length, len(resp))
        second_equals_first(
            self.document2,
            resp[0],
        )

    def test_can_read_correct_petition_doc_when_multiple_petition_docs_present(
        self,
    ):
        petition_docs = self.inst.read({
            'trial_id': self.document1['trial_id'],
            'type': 'petition',
        })
        self.assertEqual(1, len(petition_docs))
        self.assertEqual(
            self.document3['id'],
            petition_docs[0]['id'],
        )

    def test_update(self):
        new_file = self.inst_file.create({
            'file_format': 'pdf',
            's3_bucket_name': 'test-bucket',
            's3_key_name': 'key1',
        })
        new_data = {
            'trial_id': self.trial2['id'],
            'title': 'New title',
            'type': DOCUMENT_TYPES['institution'],
            'file_id': new_file['id'],
            'has_smart_doc': True,
        }
        resp = self.inst.update(
            id=self.document1['id'],
            params=new_data,
        )
        second_equals_first(
            {
                'id': self.document1['id'],
                'trial_id': new_data['trial_id'],
                'ptab_document_id': self.document1['ptab_document_id'],
                'type': new_data['type'],
                'title': new_data['title'],
                'file_id': new_data['file_id'],
                'filing_date': None,
                'has_smart_doc': new_data['has_smart_doc'],
            },
            resp,
        )

    def test_update_has_smart_doc(self):
        new_data = {'has_smart_doc': True}
        resp = self.inst.update(
            id=self.document1['id'],
            params=new_data,
        )
        second_equals_first(
            {
                'id': self.document1['id'],
                'has_smart_doc': new_data['has_smart_doc'],
            },
            resp,
        )

    def test_update_exhibit_number(self):
        new_data = {'exhibit_number': '800001'}
        resp = self.inst.update(
            id=self.document1['id'],
            params=new_data,
        )
        second_equals_first(
            {
                'id': self.document1['id'],
                'exhibit_number': new_data['exhibit_number'],
            },
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
        response = self.inst.read({'id': self.document1['id']})
        self.assertEqual(len(response), 1)
        response = self.inst.delete(id=self.document1['id'])
        self.assertEqual(response, 'Successfully deleted')
        response = self.inst.read({'id': self.document1['id']})
        self.assertEqual(len(response), 0)

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'trial_id': self.trial1['id'],
                'title': 'Doc 1',
                'filing_date': '2017-07-05',
                'type': 'original_final',
            }
        )

    def test_upsert_creates_new_entry(self):
        data = {
            'trial_id': self.trial1['id'],
            'ptab_document_id': 3333,
            'title': 'Doc2',
            'filing_date': '2017-07-05',
            'type': 'some-document-type',
            'document_number': '3000',
        }
        resp = self.inst.upsert(data)
        second_equals_first(
            {
                'trial_id': self.trial1['id'],
                'ptab_document_id': data['ptab_document_id'],
                'title': data['title'],
                'filing_date': '2017-07-05T00:00:00+00:00',
                'type': data['type'],
                'file_id': None,
                'document_number': data['document_number'],
            },
            resp,
        )

    def test_upsert_updates_existing_row(self):
        data = {
            'trial_id': self.trial1['id'],
            'ptab_document_id': 3333,
            'title': 'Doc2',
            'filing_date': '2017-07-05',
            'type': 'some-document-type',
        }
        resp = self.inst.upsert(data)
        second_equals_first(
            {
                'trial_id': self.trial1['id'],
                'ptab_document_id': data['ptab_document_id'],
                'title': data['title'],
                'filing_date': '2017-07-05T00:00:00+00:00',
                'type': data['type'],
                'file_id': None,
                'document_number': None,
            },
            resp,
        )

        new_data = {
            'trial_id': self.trial1['id'],
            'ptab_document_id': 3333,
            'title': 'Doc2',
            'filing_date': '2017-07-05',
            'type': 'other-document-type',
            'document_number': '3000',
        }
        response = self.inst.upsert(params=new_data)
        second_equals_first(
            {
                'trial_id': self.trial1['id'],
                'ptab_document_id': data['ptab_document_id'],
                'title': data['title'],
                'filing_date': '2017-07-05T00:00:00+00:00',
                'type': new_data['type'],
                'file_id': None,
                'document_number': new_data['document_number'],
            },
            response,
        )

    def test_bulk_create(self):
        mock_document1 = {
            'trial_id': self.trial1['id'],
            'ptab_document_id': 34545,
            'title': 'Some doc1',
            'filing_date': '2017-07-05',
            'type': 'other-document-type',
        }
        mock_document2 = {
            'trial_id': self.trial1['id'],
            'ptab_document_id': 345999,
            'title': 'Some doc2',
            'filing_date': '2017-07-05',
            'type': 'other-document-type',
        }
        mappings = [
            mock_document1,
            mock_document2,
        ]
        response = self.inst.read({})
        self.assertEqual(3, len(response))

        self.inst.bulk_create(mappings)
        response = self.inst.read({})
        self.assertEqual(5, len(response))
