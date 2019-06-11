from datetime import datetime
from unittest import TestCase
from dateutil.parser import parse
from uw_bridge.models import BridgeUser, BridgeCustomField, BridgeUserRole


class TestBridgeModel(TestCase):

    def test_bridge_custom_field(self):
        self.assertEqual(len(BridgeCustomField.POS1), 5)
        bcf = BridgeCustomField(value_id="1",
                                field_id="5",
                                name=BridgeCustomField.REGID_NAME,
                                value="787")
        self.assertEqual(bcf.to_json(),
                         {'id': '1',
                          'value': '787',
                          'custom_field_id': '5'})

        self.assertTrue(bcf.is_regid())
        self.assertEqual(bcf.value, '787')
        self.assertIsNotNone(str(bcf))

        bcf = BridgeCustomField(field_id="5",
                                name=BridgeCustomField.REGID_NAME,
                                value="787")
        self.assertEqual(bcf.to_json(),
                         {'custom_field_id': '5',
                          'value': '787'})
        self.assertIsNotNone(str(bcf))

    def test_bridge_user(self):
        user = BridgeUser(netid="iamstudent",
                          email="iamstudent@uw.edu",
                          full_name="Iam Student",
                          department="XYZ",
                          job_title="y",
                          manager_netid="mana",
                          bridge_id=1)
        self.assertEqual(user.to_json(),
                         {"id": 1,
                          'uid': 'iamstudent@uw.edu',
                          'email': 'iamstudent@uw.edu',
                          'full_name': 'Iam Student',
                          'manager_id': "uid:mana@uw.edu",
                          'department': "XYZ",
                          'job_title': "y"})

        self.assertEqual(user.get_uid(), "iamstudent@uw.edu")
        self.assertIsNotNone(str(user))
        self.assertTrue(user.has_bridge_id())
        self.assertFalse(user.has_last_name())
        self.assertFalse(user.has_first_name())
        self.assertTrue(user.has_manager())
        self.assertFalse(user.is_deleted())
        self.assertFalse(user.has_course_summary())
        self.assertFalse(user.no_learning_history())
        self.assertFalse(user.has_custom_field())

        user.updated_at = parse("2016-08-08T13:58:20.635-07:00")
        self.assertIsNotNone(str(user))

        user.first_name = "Iam A"
        user.last_name = "Student"
        user.manager_netid = None
        user.manager_id = 0
        user.bridge_id = 0
        self.assertEqual(user.get_sortable_name(), "Student, Iam A")
        self.assertTrue(user.has_last_name())
        self.assertTrue(user.has_first_name())
        self.assertFalse(user.has_manager())
        self.assertEqual(
            user.to_json(),
            {
             'email': 'iamstudent@uw.edu',
             'first_name': 'Iam A',
             'full_name': 'Iam Student',
             'last_name': 'Student',
             'department': "XYZ",
             'job_title': "y",
             'sortable_name': 'Student, Iam A',
             'uid': 'iamstudent@uw.edu'})

        user.completed_courses_count = 3
        self.assertTrue(user.has_course_summary())
        self.assertFalse(user.no_learning_history())
        self.assertIsNotNone(str(user))

        regid = BridgeCustomField(
            field_id="5",
            value_id="1",
            name=BridgeCustomField.REGID_NAME,
            value="12345678901234567890123456789012")
        eid = BridgeCustomField(
            value_id="2",
            field_id="6",
            name=BridgeCustomField.EMPLOYEE_ID_NAME,
            value="123456789")

        user.custom_fields[regid.name] = regid
        user.custom_fields[eid.name] = eid
        self.assertTrue(user.has_custom_field())
        self.assertEqual(len(user.custom_fields), 2)
        self.assertEqual(
            user.get_custom_field(BridgeCustomField.REGID_NAME).value,
            "12345678901234567890123456789012")

        self.assertIsNotNone(str(user))

        self.assertEqual(
            user.custom_fields_json(),
            [{'value': '12345678901234567890123456789012',
              'custom_field_id': '5',
              'id': '1'},
             {'value': '123456789',
              'custom_field_id': '6',
              'id': '2'}])

        user.bridge_id = 123
        self.assertEqual(
            user.to_json_patch(),
            {'user': {
                'uid': 'iamstudent@uw.edu',
                'id': 123,
                'email': 'iamstudent@uw.edu',
                'first_name': 'Iam A',
                'last_name': 'Student',
                'full_name': 'Iam Student',
                'sortable_name': 'Student, Iam A',
                'department': 'XYZ',
                'job_title': 'y',
                'custom_field_values': [
                    {'value': '12345678901234567890123456789012',
                     'custom_field_id': '5',
                     'id': '1'},
                    {'value': '123456789',
                     'custom_field_id': '6',
                     'id': '2'}]}})

        user.manager_id = 1
        self.assertEqual(
            user.to_json_post(),
            {'users': [{
                'uid': 'iamstudent@uw.edu',
                'id': 123,
                'email': 'iamstudent@uw.edu',
                'first_name': 'Iam A',
                'last_name': 'Student',
                'full_name': 'Iam Student',
                'sortable_name': 'Student, Iam A',
                'department': 'XYZ',
                'job_title': 'y',
                'manager_id': 1,
                'custom_field_values': [
                    {'value': '12345678901234567890123456789012',
                     'custom_field_id': '5',
                     'id': '1'},
                    {'value': '123456789',
                     'custom_field_id': '6',
                     'id': '2'}]}]})

    def test_bridge_user_role(self):
        role1 = BridgeUserRole(role_id='9a0d0b25', name='Campus Admin')
        self.assertEqual(role1.to_json(),
                         {'id': '9a0d0b25', 'name': 'Campus Admin'})
        self.assertTrue(role1.is_campus_admin())

        role = BridgeUserRole(role_id='author', name='Author')
        self.assertEqual(role.to_json(),
                         {'id': 'author', 'name': 'Author'})
        self.assertTrue(role.is_author())
        self.assertIsNotNone(str(role))

        role = BridgeUserRole(role_id="account_admin", name="Account Admin")
        self.assertTrue(role.is_account_admin())

        role = BridgeUserRole(role_id="it_admin", name="IT Admin")
        self.assertTrue(role.is_it_admin())

        role = BridgeUserRole(role_id="admin", name="Admin")
        self.assertTrue(role.is_admin())
