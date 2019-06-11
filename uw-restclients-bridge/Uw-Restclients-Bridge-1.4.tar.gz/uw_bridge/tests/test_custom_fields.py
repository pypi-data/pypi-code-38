from unittest import TestCase
from uw_bridge.models import BridgeCustomField
from uw_bridge.custom_fields import CustomFields
from uw_bridge.tests import fdao_bridge_override


@fdao_bridge_override
class TestBridgeCustomFields(TestCase):

    def test_customfields(self):
        cfs = CustomFields()
        self.assertEqual(len(cfs.get_fields()), 8)

        self.assertTrue(cfs.get_fields()[0].is_regid())
        self.assertTrue(cfs.get_fields()[1].is_employee_id())
        self.assertTrue(cfs.get_fields()[2].is_student_id())
        self.assertTrue(cfs.get_fields()[3].is_pos1_budget_code())
        self.assertTrue(cfs.get_fields()[4].is_pos1_job_code())
        self.assertTrue(cfs.get_fields()[5].is_pos1_job_clas())
        self.assertTrue(cfs.get_fields()[6].is_pos1_org_code())
        self.assertTrue(cfs.get_fields()[7].is_pos1_org_name())

        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.REGID_NAME), "5")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.EMPLOYEE_ID_NAME), "6")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.STUDENT_ID_NAME), "7")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS1_BUDGET_CODE), "11")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS1_JOB_CODE), "12")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS1_JOB_CLAS), "13")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS1_ORG_CODE), "14")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS1_ORG_NAME), "15")

        custom_field = cfs.new_custom_field(
            BridgeCustomField.REGID_NAME,
            '12345678901234567890123456789012')
        self.assertTrue(custom_field.is_regid())
        self.assertEqual(custom_field.to_json_short(),
                         {'value': '12345678901234567890123456789012',
                          'name': 'regid'})
        self.assertIsNotNone(str(custom_field))

        custom_field.value_id = "34536456"
        self.assertEqual(custom_field.to_json(),
                         {'value': '12345678901234567890123456789012',
                          'id': '34536456',
                          'custom_field_id': '5'})
