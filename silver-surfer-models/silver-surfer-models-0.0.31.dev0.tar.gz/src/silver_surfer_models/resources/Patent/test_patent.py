from marshmallow import ValidationError
from parameterized import parameterized
from sqlalchemy.exc import IntegrityError

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.Patent import (
    Patent,
    PatentNotFoundException,
)


class PatentResourceTestCase(TestCase):
    def setUp(self):
        super(PatentResourceTestCase, self).setUp()
        self.inst = Patent()
        self.patent1 = self.inst.create({
            'patent_number': '1000',
            'jurisdiction': 'USPAT',
            'app_grp_art_number': '5000',
            'grant_date': '2015/10/11',
            'app_status_date': '2015/10/13',
            'patent_pdf_url': 'https://pimg-fpiw.uspto.gov/fdd/36/39.pdf',
        })

    def test_create_validation_error_missing_fields(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {},
        )

    def test_create_violates_unique_constraint(self):
        self.assertRaises(
            IntegrityError,
            self.inst.create,
            {
                'patent_number': self.patent1['patent_number'],
                'jurisdiction': self.patent1['jurisdiction'],
                'app_grp_art_number': '123',
            },
        )

    def test_create_base(self):
        data = {
            'patent_number': '2000',
            'jurisdiction': 'USPAT',
            'app_grp_art_number': '2222',
        }
        response = self.inst.create(data)
        second_equals_first(data, response)

    def test_create(self):
        data = {
            'patent_number': '2000',
            'jurisdiction': 'USPAT',
            'app_grp_art_number': '2222',
            'primary_identifier': 'US2000',
            'grant_date': '2017/03/01',
        }
        response = self.inst.create(data)
        self.assertEqual(data['patent_number'], response['patent_number'])
        self.assertEqual(
            data['app_grp_art_number'],
            response['app_grp_art_number'],
        )
        self.assertEqual(
            data['primary_identifier'],
            response['primary_identifier'],
        )
        self.assertEqual(
            '2017-03-01T00:00:00+00:00',
            response['grant_date'],
        )

    def test_read_validation_error_blank_app_grp_art_number(self):
        self.assertRaises(
            ValidationError,
            self.inst.read,
            {'app_grp_art_number': ''},
        )

    def test_read_all(self):
        response = self.inst.read({})
        self.assertEqual(len(response), 1)

    def test_read_w_params(self):
        # setup
        self.inst.create({
            'patent_number': '2000',
            'jurisdiction': 'USPAT',
            'app_grp_art_number': '2222',
            'primary_identifier': 'US2000',
        })

        response = self.inst.read({})
        self.assertEqual(len(response), 2)

        response = self.inst.read({'patent_number': '1000'})
        self.assertEqual(len(response), 1)

        response = self.inst.read({'app_grp_art_number': '2222'})
        self.assertEqual(len(response), 1)

        response = self.inst.read({'primary_identifier': 'US2000'})
        self.assertEqual(len(response), 1)

    def test_delete_not_found(self):
        invalid_id = 99999
        self.assertRaises(
            PatentNotFoundException,
            self.inst.delete,
            invalid_id,
        )

    def test_delete(self):
        data = self.inst.read({'id': self.patent1['id']})
        self.assertEqual(len(data), 1)
        response = self.inst.delete(id=self.patent1['id'])
        self.assertEqual(response, 'Successfully deleted')
        data = self.inst.read({'id': self.patent1['id']})
        self.assertEqual(len(data), 0)

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {'app_grp_art_number': ''},
        )

    def test_upsert_creates_new_entry(self):
        data = {
            'patent_number': '21321',
            'jurisdiction': 'USPAT',
            'app_grp_art_number': '123123',
        }
        self.assertEqual(1, len(self.inst.read({})))
        resp = self.inst.upsert(data)
        self.assertEqual(2, len(self.inst.read({})))
        second_equals_first(
            data,
            resp,
        )

    def test_upsert_updates_existing_row(self):
        data = {
            'patent_number': '21321',
            'jurisdiction': 'USPAT',
            'app_grp_art_number': '123123',
            'kind_code': 'something',
        }
        self.assertEqual(1, len(self.inst.read({})))
        resp = self.inst.upsert(data)
        self.assertEqual(2, len(self.inst.read({})))
        second_equals_first(
            data,
            resp,
        )

        new_data = {
            'patent_number': resp['patent_number'],
            'jurisdiction': resp['jurisdiction'],
            'app_grp_art_number': '123123',
            'abstract_text': 'Some abstract text',
        }
        response = self.inst.upsert(params=new_data)
        self.assertEqual(2, len(self.inst.read({})))
        expected_data = {
            **data,
            **new_data,
        }
        second_equals_first(
            expected_data,
            response,
        )

    @parameterized.expand([
        ('1599', 0),
        ('1600', 1),
        ('1601', 1),
        ('16100', 0),
        ('1700', 0),
        ('1701', 0),
        ('12316', 0),
    ])
    def test_pharma_patents(self, app_grp_art_number, expected_length):
        self.inst.create({
            'patent_number': '2000',
            'jurisdiction': 'USPAT',
            'app_grp_art_number': app_grp_art_number,
        })
        pharma_patents = self.inst.pharma_patents()
        self.assertEqual(expected_length, len(pharma_patents))
