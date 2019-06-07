from marshmallow import ValidationError
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.PatentCompound import (
    PatentCompound,
)
from src.silver_surfer_models.resources.Patent import Patent
from src.silver_surfer_models.resources.File import File


class PatentCompoundResourceTestCase(TestCase):
    def setUp(self):
        super(PatentCompoundResourceTestCase, self).setUp()
        self.inst_patent = Patent()
        self.inst_file = File()
        self.inst = PatentCompound()
        self.file1 = self.inst_file.create({
            'file_format': 'txt',
            's3_bucket_name': 'test-bucket',
            's3_key_name': 'key1',
        })
        self.patent1 = self.inst_patent.create({
            'patent_number': '1000',
            'app_grp_art_number': '5000',
            'jurisdiction': 'USPAT',
        })
        self.patent2 = self.inst_patent.create({
            'patent_number': '2000',
            'app_grp_art_number': '5000',
            'jurisdiction': 'USPAT',
        })
        self.patent_compound1 = self.inst.create({
            'patent_id': self.patent1['id'],
            'cid': 'some cid',
            'compound_name': 'some compound_name',
            'iupac_name': 'some iupac_name',
            'molecular_formula': 'some molecular_formula',
            'molecular_weight': 'some molecular_weight',
            'structure_file_id': self.file1['id'],
        })

    def test_create_validation_error_missing_fields(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {},
        )

    def test_create_validation_error_blank_cid(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {
                'patent_id': 123,
                'cid': '',
                'compound_name': 'some compound_name',
                'iupac_name': 'some iupac_name',
                'molecular_formula': 'some molecular_formula',
                'molecular_weight': 'some molecular_weight',
            },
        )

    def test_create_duplicate_patent_id(self):
        self.assertRaises(
            Exception,
            self.inst.create,
            {
                'patent_id': self.patent_compound1['patent_id'],
                'cid': self.patent_compound1['cid'],
                'compound_name': 'some compound_name',
                'iupac_name': 'some iupac_name',
                'molecular_formula': 'some molecular_formula',
                'molecular_weight': 'some molecular_weight',
            }
        )

    def test_create(self):
        new_data = {
            'patent_id': self.patent2['id'],
            'cid': 'some cid',
            'compound_name': 'some compound_name',
            'iupac_name': 'some iupac_name',
            'molecular_formula': 'some molecular_formula',
            'molecular_weight': 'some molecular_weight',
            'structure_file_id': self.file1['id'],
        }
        response = self.inst.create(new_data)
        second_equals_first(new_data, response)

    def test_read_validation_error_blank_cid(self):
        self.assertRaises(
            ValidationError,
            self.inst.read,
            {'cid': ''},
        )

    def test_read_all(self):
        response = self.inst.read({})
        self.assertEqual(len(response), 1)

    def test_read_w_params(self):
        # setup
        self.inst.create({
            'patent_id': self.patent2['id'],
            'cid': 'some cid2',
            'compound_name': 'some compound_name2',
            'iupac_name': 'some iupac_name2',
            'molecular_formula': 'some molecular_formula',
            'molecular_weight': 'some molecular_weight',
            'structure_file_id': self.file1['id'],
        })

        response = self.inst.read({})
        self.assertEqual(len(response), 2)

        response = self.inst.read({'patent_id': self.patent1['id']})
        self.assertEqual(len(response), 1)

        response = self.inst.read({'cid': self.patent_compound1['cid']})
        self.assertEqual(len(response), 1)

        response = self.inst.read({
            'compound_name': self.patent_compound1['compound_name'],
        })
        self.assertEqual(len(response), 1)

        response = self.inst.read({
            'iupac_name': self.patent_compound1['iupac_name'],
        })
        self.assertEqual(len(response), 1)

    def test_one_raises_MultipleResultsFound(self):
        # setup
        self.inst.create({
            'patent_id': self.patent2['id'],
            'cid': 'some cid',
            'compound_name': 'some compound_name2',
            'iupac_name': 'some iupac_name2',
            'molecular_formula': 'some molecular_formula',
            'molecular_weight': 'some molecular_weight',
            'structure_file_id': self.file1['id'],
        })

        self.assertRaises(
            MultipleResultsFound,
            self.inst.one,
            {'cid': self.patent_compound1['cid']},
        )

    def test_one_raises_NoResultFound(self):
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'cid': '123123'},
        )
