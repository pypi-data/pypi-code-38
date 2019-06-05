from marshmallow import ValidationError
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.OrangeBookProduct import (
    OrangeBookProduct,
    OrangeBookProductNotFoundException,
)


class OrangeBookProductResourceTestCase(TestCase):
    def setUp(self):
        super(OrangeBookProductResourceTestCase, self).setUp()
        self.inst = OrangeBookProduct()
        self.ob_product1 = self.inst.create({
            'appl_no': '78907',
            'appl_type': 'A',
            'applicant': 'SPECGX LLC',
            'applicant_full_name': 'SPECGX LLC',
            'approval_date': 'Oct 30, 2009',
            'dosage_form': 'TROCHE/LOZENGE',
            'ingredient': 'FENTANYL CITRATE',
            'product_no': '6',
            'rld': 'No',
            'rs': 'No',
            'route_of_administration': 'TRANSMUCOSAL',
            'strength': 'EQ 1.6MG BASE',
            'te_code': 'AB',
            'trade_name': 'FENTANYL CITRATE',
            'type': 'RX'
        })

    def test_create_validation_error_missing_fields(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {},
        )

    @parameterized.expand([
        'appl_no',
        'product_no',
    ])
    def test_create_validation_error_blank(self, field_name):
        base_data = {
            'appl_no': '213123',
            'appl_type': 'A',
            'applicant': 'SPECGX LLC',
            'applicant_full_name': 'SPECGX LLC',
            'approval_date': 'Oct 30, 2009',
            'dosage_form': 'TROCHE/LOZENGE',
            'ingredient': 'FENTANYL CITRATE',
            'product_no': '6',
            'rld': 'No',
            'rs': 'No',
            'route_of_administration': 'TRANSMUCOSAL',
            'strength': 'EQ 1.6MG BASE',
            'te_code': 'AB',
            'trade_name': 'FENTANYL CITRATE',
            'type': 'RX',
        }
        new_data = {
            field_name: '',
        }
        data = {
            **base_data,
            **new_data,
        }
        self.assertRaises(
            ValidationError,
            self.inst.create,
            data,
        )

    def test_create_duplicate_appl_no(self):
        self.assertRaises(
            Exception,
            self.inst.create,
            {
                'appl_no': self.ob_product1['appl_no'],
                'appl_type': 'A',
                'applicant': 'SPECGX LLC',
                'applicant_full_name': 'SPECGX LLC',
                'approval_date': 'Oct 30, 2009',
                'dosage_form': 'TROCHE/LOZENGE',
                'ingredient': 'FENTANYL CITRATE',
                'product_no': '6',
                'rld': 'No',
                'rs': 'No',
                'route_of_administration': 'TRANSMUCOSAL',
                'strength': 'EQ 1.6MG BASE',
                'te_code': 'AB',
                'trade_name': 'FENTANYL CITRATE',
                'type': 'RX'
            },
        )

    def test_create(self):
        data = {
            'appl_no': '123123',
            'appl_type': 'A',
            'applicant': 'SPECGX LLC',
            'applicant_full_name': 'SPECGX LLC',
            'approval_date': 'Oct 30, 2009',
            'dosage_form': 'TROCHE/LOZENGE',
            'ingredient': 'FENTANYL CITRATE',
            'product_no': '6',
            'rld': 'No',
            'rs': 'No',
            'route_of_administration': 'TRANSMUCOSAL',
            'strength': 'EQ 1.6MG BASE',
            'te_code': 'AB',
            'trade_name': 'FENTANYL CITRATE',
            'type': 'RX',
        }
        response = self.inst.create(data)
        data.pop('approval_date')
        second_equals_first(
            data,
            response,
        )

    def test_read_validation_error_blank_appl_no(self):
        self.assertRaises(
            ValidationError,
            self.inst.read,
            {'appl_no': ''},
        )

    def test_read_all(self):
        response = self.inst.read({})
        self.assertEqual(len(response), 1)

    @parameterized.expand([
        ('appl_no', 1),
        ('product_no', 2),
        ('trade_name', 2),
    ])
    def test_read_w_params(self, attr, expected_length):
        # setup
        new_ob_product = self.inst.create({
            'appl_no': '123123',
            'appl_type': 'A',
            'applicant': 'SPECGX LLC',
            'applicant_full_name': 'SPECGX LLC',
            'approval_date': 'Oct 30, 2009',
            'dosage_form': 'TROCHE/LOZENGE',
            'ingredient': 'FENTANYL CITRATE',
            'product_no': self.ob_product1['product_no'],
            'rld': 'No',
            'rs': 'No',
            'route_of_administration': 'TRANSMUCOSAL',
            'strength': 'EQ 1.6MG BASE',
            'te_code': 'AB',
            'trade_name': 'FENTANYL',
            'type': 'RX',
        })
        self.inst.create({
            'appl_no': '324234',
            'appl_type': 'A',
            'applicant': 'SPECGX LLC',
            'applicant_full_name': 'SPECGX LLC',
            'approval_date': 'Oct 30, 2009',
            'dosage_form': 'TROCHE/LOZENGE',
            'ingredient': 'FENTANYL CITRATE',
            'product_no': '123324234',
            'rld': 'No',
            'rs': 'No',
            'route_of_administration': 'TRANSMUCOSAL',
            'strength': 'EQ 1.6MG BASE',
            'te_code': 'AB',
            'trade_name': 'Copaxone',
            'type': 'RX',
        })

        response = self.inst.read({})
        self.assertEqual(3, len(response))

        response = self.inst.read({attr: new_ob_product[attr]})
        self.assertEqual(expected_length, len(response))

    def test_update_not_found(self):
        invalid_id = 99999
        args = []
        kwargs = {'id': invalid_id, 'params': {
            'appl_no': '123123',
            'appl_type': 'A',
            'applicant': 'SPECGX LLC',
            'applicant_full_name': 'SPECGX LLC',
            'approval_date': 'Oct 30, 2009',
            'dosage_form': 'TROCHE/LOZENGE',
            'ingredient': 'FENTANYL CITRATE',
            'product_no': self.ob_product1['product_no'],
            'rld': 'No',
            'rs': 'No',
            'route_of_administration': 'TRANSMUCOSAL',
            'strength': 'EQ 1.6MG BASE',
            'te_code': 'AB',
            'trade_name': 'FENTANYL CITRATE',
            'type': 'RX',
        }}
        self.assertRaises(
            OrangeBookProductNotFoundException,
            self.inst.update,
            *args,
            **kwargs
        )

    @parameterized.expand([
        'appl_no',
        'product_no',
    ])
    def test_update_validation_error_blank_appl_no(self, field_name):
        args = []
        kwargs = {
            'id': self.ob_product1['id'],
            'params': {
                'appl_no': self.ob_product1['appl_no'],
                'appl_type': 'A',
                'applicant': 'SPECGX LLC',
                'applicant_full_name': 'SPECGX LLC',
                'approval_date': 'Oct 30, 2009',
                'dosage_form': 'TROCHE/LOZENGE',
                'ingredient': 'FENTANYL CITRATE',
                'product_no': self.ob_product1['product_no'],
                'rld': 'No',
                'rs': 'No',
                'route_of_administration': 'TRANSMUCOSAL',
                'strength': 'EQ 1.6MG BASE',
                'te_code': 'AB',
                'trade_name': 'FENTANYL CITRATE',
                'type': 'RX',
            },
        }
        kwargs['params'][field_name] = ''
        self.assertRaises(
            ValidationError,
            self.inst.update,
            *args,
            **kwargs
        )

    @parameterized.expand([
        'appl_no',
        'product_no',
    ])
    def test_update(self, field_name):
        new_data = {
            'appl_no': '2000',
            'appl_type': 'ABBB',
            'applicant': 'SPECGX LLC',
            'applicant_full_name': 'SPECGX LLC',
            'approval_date': 'Oct 30, 2009',
            'dosage_form': 'TROCHE/LOZENGE',
            'ingredient': 'FENTANYL CITRATE',
            'product_no': '123123123',
            'rld': 'No',
            'rs': 'No',
            'route_of_administration': 'TRANSMUCOSAL',
            'strength': 'EQ 1.6MG BASE',
            'te_code': 'AB',
            'trade_name': 'FENTANYL CITRATE',
            'type': 'RX',
        }
        response = self.inst.update(
            id=self.ob_product1['id'],
            params=new_data,
        )
        self.assertEqual(response['id'], self.ob_product1['id'])
        self.assertEqual(
            response[field_name],
            self.ob_product1[field_name],
        )
        self.assertEqual(
            response['appl_type'],
            new_data['appl_type'],
        )

    @parameterized.expand([
        ('appl_no', '123'),
        ('product_no', '123'),
    ])
    def test_update_partial(self, immutable_field, value):
        new_data = {
            immutable_field: value,
            'appl_type': 'NM',
        }
        response = self.inst.update(
            id=self.ob_product1['id'],
            params=new_data,
        )
        self.assertEqual(response['id'], self.ob_product1['id'])
        self.assertEqual(
            response[immutable_field],
            self.ob_product1[immutable_field],
        )
        self.assertEqual(
            response['appl_type'],
            new_data['appl_type'],
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {'appl_no': ''},
        )

    def test_upsert_creates_new_entry(self):
        data = {
            'appl_no': '2000',
            'appl_type': 'ABBB',
            'applicant': 'SPECGX LLC',
            'applicant_full_name': 'SPECGX LLC',
            'approval_date': 'Oct 30, 2009',
            'dosage_form': 'TROCHE/LOZENGE',
            'ingredient': 'FENTANYL CITRATE',
            'product_no': self.ob_product1['product_no'],
            'rld': 'No',
            'rs': 'No',
            'route_of_administration': 'TRANSMUCOSAL',
            'strength': 'EQ 1.6MG BASE',
            'te_code': 'AB',
            'trade_name': 'FENTANYL CITRATE',
            'type': 'RX',
        }
        self.assertEqual(1, len(self.inst.read({})))
        self.inst.upsert(data)

        resp = self.inst.read({})
        self.assertEqual(2, len(resp))
        appl_nos = [r['appl_no'] for r in resp]
        self.assertIn(self.ob_product1['appl_no'], appl_nos)
        self.assertIn(data['appl_no'], appl_nos)

    def test_upsert_updates_existing_row(self):
        new_data = {
            'appl_no': self.ob_product1['appl_no'],
            'appl_type': 'ABBB',
            'applicant': 'SPECGX LLC',
            'applicant_full_name': 'SPECGX LLC',
            'approval_date': '30-Oct-19',
            'dosage_form': 'TROCHE/LOZENGE',
            'ingredient': 'FENTANYL CITRATE',
            'product_no': self.ob_product1['product_no'],
            'rld': 'No',
            'rs': 'No',
            'route_of_administration': 'TRANSMUCOSAL',
            'strength': 'EQ 1.6MG BASE',
            'te_code': 'AB',
            'trade_name': 'FENTANYL CITRATE',
            'type': 'RX',
        }
        response = self.inst.upsert(params=new_data)
        self.assertEqual(1, len(self.inst.read({})))
        new_data.pop('approval_date')
        second_equals_first(
            new_data,
            response,
        )
