from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.silver_surfer_models.resources.PacerCase import PacerCase


class PacerCaseResourceTestCase(TestCase):
    def setUp(self):
        super(PacerCaseResourceTestCase, self).setUp()
        self.inst = PacerCase()

        self.pacer_case1 = self.inst.create({
            'case_no': '2:17-cv-05314-SDW-LDW',
            'court_id': 'njd',
            'pacer_case_external_id': '1000',
            'cause': '15:1126 Patent Infringement',
            'county': 'Union',
            'defendant': "DR. REDDY'S LABORATORIES, LTD.",
            'disposition': "Something",
            'filed_date': '07/20/2017',
            'flags': 'ANDA,SCHEDO',
            'jurisdiction': 'Federal Question',
            'lead_case': 'None',
            'nature_of_suit': '835',
            'office': 'Newark',
            'plaintiff': 'CELGENE CORPORATION',
            'related_case': '2:16-cv-07704-SDW-LDW',
            'terminated_date': '09/20/2017',
        })

        self.pacer_case2 = self.inst.create({
            'case_no': '3:17-cv-05314-SDW-LDW',
            'court_id': 'njd',
            'pacer_case_external_id': '2000',
            'cause': '15:1126 Patent Infringement',
        })

    @parameterized.expand([
        ('case_no',),
        ('court_id',),
        ('pacer_case_external_id',),
    ])
    def test_create_validation_error_missing_field(self, field_to_pop):
        base_data = {
            'case_no': '3:17-cv-05314-SDW-LDW',
            'court_id': 'njd',
            'pacer_case_external_id': '351755',
            'cause': '15:1126 Patent Infringement',
        }
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
            {
                'case_no': '4:17-cv-05314-SDW-LDW',
                'court_id': self.pacer_case1['court_id'],
                'pacer_case_external_id': (
                    self.pacer_case1['pacer_case_external_id']),
                'cause': '15:1126 Patent Infringement',
            },
        )

    def test_create(self):
        data = {
            'case_no': '100:17-cv-05314-SDW-LDW',
            'court_id': 'njd',
            'pacer_case_external_id': '10000',
            'cause': '15:1126 Patent Infringement',
        }
        resp = self.inst.create(data)
        second_equals_first(data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

    @parameterized.expand([
        ('id', 'pacer_case1', 'id', 1),
        ('case_no', 'pacer_case1', 'case_no', 1),
        ('court_id', 'pacer_case1', 'court_id', 2),
        ('pacer_case_external_id', 'pacer_case1', 'pacer_case_external_id', 1),
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

    def test_read_w_params_ids(self):
        resp = self.inst.read({'ids': []})
        self.assertEqual(0, len(resp))

        resp = self.inst.read({'ids': [self.pacer_case1['id']]})
        self.assertEqual(1, len(resp))
        second_equals_first(
            self.pacer_case1,
            resp[0]
        )

    @parameterized.expand([
        ('id', 999, NoResultFound),
        ('court_id', 'njd', MultipleResultsFound),
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
        ('case_no',),
        ('pacer_case_external_id',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.pacer_case1[field_name],
        })
        second_equals_first(
            self.pacer_case1,
            resp,
        )

    def test_update(self):
        new_data = {
            'case_no': 'something new',
            'court_id': 'ny',
            'pacer_case_external_id': '9999',
            'cause': 'something new',
        }
        resp = self.inst.update(
            id=self.pacer_case1['id'],
            params=new_data,
        )
        expected_result = {
            **self.pacer_case1,
            **new_data,
            # the following fields cannot be updated
            **{
                'court_id': self.pacer_case1['court_id'],
                'pacer_case_external_id': (
                    self.pacer_case1['pacer_case_external_id']),
            },
        }

        expected_result.pop('updated_at')
        resp.pop('updated_at')
        second_equals_first(
            expected_result,
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
        response = self.inst.one({'id': self.pacer_case1['id']})
        self.inst.delete(id=response['id'])
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {'id': self.pacer_case1['id']},
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'case_no': '3:17-cv-05314-SDW-LDW',
                'pacer_case_external_id': '351755',
                'cause': '15:1126 Patent Infringement',
            }
        )

    def test_upsert_creates_new_entry(self):
        data = {
            'case_no': '3:17-cv-05314-SDW-LDW',
            'court_id': 'njd',
            'pacer_case_external_id': '351755',
            'cause': '',
            'county': 'Union',
            'defendant': "DR. REDDY'S LABORATORIES, LTD.",
            'disposition': "Something",
            'filed_date': None,
            'flags': 'ANDA,SCHEDO',
            'jurisdiction': 'Federal Question',
            'lead_case': 'None',
            'nature_of_suit': '835',
            'office': 'Newark',
            'plaintiff': 'CELGENE CORPORATION',
            'related_case': '2:16-cv-07704-SDW-LDW',
            'terminated_date': None,
        }
        self.assertEqual(2, len(self.inst.read({})))
        self.inst.upsert(data)
        self.assertEqual(3, len(self.inst.read({})))

    def test_upsert_updates_existing_row(self):
        data = {
            'case_no': '3:17-cv-05314-SDW-LDW',
            'court_id': self.pacer_case1['court_id'],
            'pacer_case_external_id': (
                self.pacer_case1['pacer_case_external_id']),
            'cause': '15:1126 Patent Infringement',
        }
        resp = self.inst.upsert(data)
        second_equals_first(
            data,
            resp,
        )
