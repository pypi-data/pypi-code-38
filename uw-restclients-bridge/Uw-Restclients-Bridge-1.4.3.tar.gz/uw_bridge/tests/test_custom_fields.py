from unittest import TestCase
from uw_bridge.models import BridgeCustomField
from uw_bridge.custom_fields import CustomFields
from uw_bridge.tests import fdao_bridge_override


@fdao_bridge_override
class TestBridgeCustomFields(TestCase):

    def test_customfields(self):
        cfs = CustomFields()
        self.assertEqual(len(cfs.get_fields()), 17)

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
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS1_UNIT_CODE), "16")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS1_LOCATION), "17")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS2_BUDGET_CODE), "21")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS2_JOB_CODE), "22")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS2_JOB_CLAS), "23")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS2_ORG_CODE), "24")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS2_ORG_NAME), "25")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS2_UNIT_CODE), "26")
        self.assertEqual(cfs.get_field_id(
            BridgeCustomField.POS2_LOCATION), "27")

        custom_field = cfs.new_custom_field(
            BridgeCustomField.REGID_NAME,
            '12345678901234567890123456789012')
        self.assertEqual(custom_field.to_json_short(),
                         {'value': '12345678901234567890123456789012',
                          'name': 'regid'})
        self.assertIsNotNone(str(custom_field))

        custom_field.value_id = "34536456"
        self.assertEqual(custom_field.to_json(),
                         {'value': '12345678901234567890123456789012',
                          'id': '34536456',
                          'custom_field_id': '5'})
