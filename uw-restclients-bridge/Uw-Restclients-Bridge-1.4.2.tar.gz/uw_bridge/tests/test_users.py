from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_bridge.models import BridgeUser, BridgeCustomField
from uw_bridge.users import Users, ADMIN_URL_PREFIX, AUTHOR_URL_PREFIX
from uw_bridge.tests import fdao_bridge_override


@fdao_bridge_override
class TestBridgeUser(TestCase):

    @classmethod
    def setUpClass(cls):
        TestBridgeUser.users = Users()

    def test_admin_id_url(self):
        self.assertEqual(TestBridgeUser.users.admin_id_url(None),
                         ADMIN_URL_PREFIX)
        self.assertEqual(TestBridgeUser.users.admin_id_url(123),
                         ADMIN_URL_PREFIX + '/123')

    def test_author_id_url(self):
        self.assertEqual(TestBridgeUser.users.author_id_url(None),
                         AUTHOR_URL_PREFIX)
        self.assertEqual(TestBridgeUser.users.author_id_url(123),
                         AUTHOR_URL_PREFIX + '/123')

    def test_admin_uid_url(self):
        self.assertEqual(TestBridgeUser.users.admin_uid_url(None),
                         ADMIN_URL_PREFIX)
        self.assertEqual(TestBridgeUser.users.admin_uid_url('staff'),
                         ADMIN_URL_PREFIX + '/uid%3Astaff%40uw%2Eedu')

    def test_author_uid_url(self):
        self.assertEqual(TestBridgeUser.users.author_uid_url(None),
                         AUTHOR_URL_PREFIX)
        self.assertEqual(TestBridgeUser.users.author_uid_url('staff'),
                         AUTHOR_URL_PREFIX + '/uid%3Astaff%40uw%2Eedu')

    def test_get_obj_from_list(self):
        users = []
        self.assertIsNone(
            TestBridgeUser.users._get_obj_from_list("test", users))

        users.append(BridgeUser(netid="eight",
                                full_name="Eight Class Student",
                                first_name="Eight Class",
                                last_name="Student",
                                email="eight@uw.edu"))
        users.append(BridgeUser(netid="eight1",
                                full_name="Eight1 Class Student",
                                first_name="Eight1 Class",
                                last_name="Student",
                                email="eight1@uw.edu"))
        self.assertIsNotNone(
            TestBridgeUser.users._get_obj_from_list("test", users))

    def test_process_apage(self):
        bridge_users = []
        bridge_users = TestBridgeUser.users._process_apage(
            {"meta": {},
             "linked": {
                 "custom_fields": [{"id": "9",
                                    "name": "Regid"}],
                 "custom_field_values": [
                     {"id": "754517",
                      "value": "6B79E4406A7D1",
                      "links": {
                          "custom_field": {"id": "9",
                                           "type": "custom_fields"}}}]},
             "users": [
                 {"id": "1",
                  "uid": "bill@uw.edu",
                  "hris_id": None,
                  "first_name": "Bill",
                  "last_name": "Smith",
                  "full_name": "Bill Smith",
                  "sortable_name": "Smith, Bill",
                  "email": "bill@uw.edu",
                  "locale": "en",
                  "roles": ["author"],
                  "name": "Bill Smith",
                  "avatar_url": None,
                  "updated_at": "2019-05-14T15:12:37.502-07:00",
                  "deleted_at": None,
                  "unsubscribed": None,
                  "welcomedAt": None,
                  "loggedInAt": "2019-05-14T10:17:34.757-07:00",
                  "passwordIsSet":False,
                  "hire_date": None,
                  "is_manager":False,
                  "job_title": "Software Engineer",
                  "bio": None,
                  "department": "Unix Engineering",
                  "anonymized": None,
                  "welcomeUrl": "...",
                  "passwordUrl": "...",
                  "next_due_date": None,
                  "completed_courses_count": 0,
                  "manager_name": None,
                  "manager_id": "10",
                  "links": {"custom_field_values": ["754517"]}}]},
            bridge_users, False)
        user = bridge_users[0]
        self.assertEqual(
            user.to_json_patch(),
            {'user': {
                'uid': 'bill@uw.edu',
                'full_name': 'Bill Smith',
                'email': 'bill@uw.edu',
                'id': 1,
                'first_name': 'Bill',
                'last_name': 'Smith',
                'sortable_name': 'Smith, Bill',
                'department': 'Unix Engineering',
                'job_title': 'Software Engineer',
                'manager_id': 10,
                "custom_field_values": [
                    {'value': '6B79E4406A7D1',
                     'custom_field_id': '9',
                     'id': '754517'}]}})

    def test_process_err(self):
        self.assertRaises(KeyError,
                          TestBridgeUser.users._process_apage,
                          {"meta": {}, "linked": {}},
                          [],
                          no_custom_fields=False)

        bridge_users = TestBridgeUser.users._process_json_resp_data(
            b'{"linked": {"custom_fields": [], "custom_field_values": []}}')
        self.assertEqual(len(bridge_users), 0)

    def test_get_user(self):
        user = TestBridgeUser.users.get_user('javerage')
        self.assertEqual(user.bridge_id, 195)
        self.assertEqual(user.first_name, "James")
        self.assertEqual(user.last_name, "Student")
        self.assertEqual(user.full_name, "James Student")
        self.assertEqual(user.get_sortable_name(),
                         "Student, James")
        self.assertEqual(user.email, "javerage@uw.edu")
        self.assertEqual(user.netid, "javerage")
        self.assertEqual(user.get_uid(), "javerage@uw.edu")
        self.assertFalse(user.is_deleted())
        self.assertEqual(
            str(user.updated_at), '2016-07-25 16:24:42.131000-07:00')
        self.assertEqual(
            str(user.logged_in_at), "2016-09-02 15:27:01.827000-07:00")
        self.assertEqual(user.next_due_date, None)
        self.assertEqual(user.completed_courses_count, 0)
        self.assertTrue(user.has_course_summary())
        self.assertTrue(user.no_learning_history())

        self.assertEqual(len(user.custom_fields), 8)
        cus_field = user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_field.value_id, "1")
        self.assertEqual(cus_field.field_id, "5")
        self.assertEqual(cus_field.name, "regid")
        self.assertEqual(cus_field.value,
                         "9136CCB8F66711D5BE060004AC494FFE")
        cus_field = user.get_custom_field(BridgeCustomField.EMPLOYEE_ID_NAME)
        self.assertEqual(cus_field.value_id, "2")
        self.assertEqual(cus_field.field_id, "6")
        self.assertEqual(cus_field.name, "employee_id")
        self.assertEqual(cus_field.value, "123456789")

        cus_field = user.get_custom_field(BridgeCustomField.STUDENT_ID_NAME)
        self.assertEqual(cus_field.value_id, "3")
        self.assertEqual(cus_field.field_id, "7")
        self.assertEqual(cus_field.name, "student_id")
        self.assertEqual(cus_field.value, "1033334")

        cus_field = user.get_custom_field(BridgeCustomField.POS1_BUDGET_CODE)
        self.assertEqual(cus_field.value_id, "4")
        self.assertEqual(cus_field.field_id, "11")
        self.assertEqual(cus_field.name, "pos1_budget_code")
        self.assertEqual(cus_field.value, "2070001000")

        self.assertEqual(len(user.roles), 3)
        self.assertTrue(user.roles[0].is_account_admin())
        self.assertTrue(user.roles[1].is_author())
        self.assertTrue(user.roles[2].is_campus_admin())
        self.assertIsNotNone(str(user))

    def test_get_user_with_deleted(self):
        user = TestBridgeUser.users.get_user_by_id(
            17637, include_deleted=False)
        self.assertIsNone(user)

        user = TestBridgeUser.users.get_user_by_id(
            17637, include_deleted=True)
        self.verify_bill(user)
        self.assertTrue(user.is_deleted())
        self.assertTrue(user.has_manager())

        cus_field = user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_field.value,
                         "FBB38FE46A7C11D5A4AE0004AC494FFE")

        self.assertRaises(DataFailureException,
                          TestBridgeUser.users.get_user, 'unknown')

        self.assertRaises(DataFailureException,
                          TestBridgeUser.users.get_user_by_id, 19567)

    def verify_bill(self, user):
        self.assertEqual(user.bridge_id, 17637)
        self.assertEqual(user.get_uid(), "bill@uw.edu")
        self.assertEqual(user.first_name, "Bill Average")
        self.assertEqual(user.last_name, "Teacher")
        self.assertEqual(user.full_name, "Bill Average Teacher")
        self.assertEqual(user.get_sortable_name(), "Teacher, Bill Average")
        self.assertEqual(user.email, "bill@u.washington.edu")
        self.assertEqual(user.netid, "bill")
        self.assertTrue(user.is_manager)

    def test_get_all_users_url(self):
        self.assertEqual(
            TestBridgeUser.users._get_all_users_url(False, True),
            "/api/author/users?includes%5B%5D=&limit=1000")
        self.assertEqual(
            TestBridgeUser.users._get_all_users_url(False, False),
            "/api/author/users?includes%5B%5D=custom_fields&limit=1000")
        self.assertEqual(
            TestBridgeUser.users._get_all_users_url(True, False),
            "/api/author/users?includes%5B%5D=custom_fields&"
            "includes%5B%5D=course_summary&limit=1000")

    def test_get_alluser(self):
        user_list = TestBridgeUser.users.get_all_users(
            include_course_summary=True, no_custom_fields=False)
        self.assertEqual(len(user_list), 2)
        user = user_list[0]
        self.assertEqual(user.full_name, "Eight Class Student")
        self.assertEqual(user.bridge_id, 106)
        cus_field = user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_field.value,
                         "12345678901234567890123456789012")
        user = user_list[1]
        self.assertEqual(user.full_name, "James Student")
        self.assertEqual(user.bridge_id, 195)
        cus_field = user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_field.value,
                         "9136CCB8F66711D5BE060004AC494FFE")

        user_list = TestBridgeUser.users.get_all_users(
            include_course_summary=False, no_custom_fields=False)
        self.assertEqual(len(user_list), 3)
        self.assertEqual(user_list[0].bridge_id, 106)
        self.assertEqual(user_list[1].bridge_id, 195)
        self.assertEqual(user_list[2].bridge_id, 17)
        user = user_list[2]
        self.assertEqual(user.full_name, "None Average Student")
        self.assertEqual(user.bridge_id, 17)
        cus_field = user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_field.value,
                         "00000000000000000000000000000001")

        user_list = TestBridgeUser.users.get_all_users()
        self.assertEqual(len(user_list), 3)
        self.assertEqual(user_list[0].bridge_id, 106)
        self.assertEqual(user_list[1].bridge_id, 195)
        self.assertEqual(user_list[2].bridge_id, 17)
        self.assertEqual(len(user_list[2].custom_fields), 0)

    def test_add_user(self):
        regid = "12345678901234567890123456789012"
        cus_fie = TestBridgeUser.users.custom_fields.new_custom_field(
            BridgeCustomField.REGID_NAME, regid)

        user = BridgeUser()
        user.netid = "eight"
        user.full_name = "Eight Class Student"
        user.first_name = "Eight Class"
        user.last_name = "Student"
        user.email = "eight@uw.edu"
        user.custom_fields[cus_fie.name] = cus_fie

        added = TestBridgeUser.users.add_user(user)
        self.assertEqual(added.bridge_id, 123)
        self.assertEqual(added.first_name, "Eight Class")
        self.assertEqual(added.last_name, "Student")
        self.assertEqual(added.full_name, "Eight Class Student")
        self.assertEqual(added.get_sortable_name(), "Student, Eight Class")
        self.assertEqual(added.email, "eight@uw.edu")
        self.assertEqual(added.netid, "eight")
        self.assertEqual(added.get_uid(), "eight@uw.edu")
        self.assertEqual(
            str(added.updated_at), '2016-09-06 21:42:48.821000-07:00')

    def test_delete_user(self):
        self.assertTrue(TestBridgeUser.users.delete_user("javerage"))
        self.assertTrue(TestBridgeUser.users.delete_user_by_id(195))
        try:
            reps = TestBridgeUser.users.delete_user("staff")
        except Exception as ex:
            self.assertEqual(ex.status, 404)

    def test_upd_uid_req_body(self):
        self.assertEqual(TestBridgeUser.users._upd_uid_req_body("netid"),
                         '{"user":{"uid":"netid@uw.edu"}}')

    def test_change_uid(self):
        self.assertRaises(DataFailureException,
                          TestBridgeUser.users.change_uid,
                          195, "bill")

        user = TestBridgeUser.users.change_uid(17637, "bill")
        self.verify_uid(user)
        self.assertEqual(len(user.custom_fields), 0)

        user = TestBridgeUser.users.replace_uid("bill", "bill")
        self.verify_uid(user)
        self.assertEqual(len(user.custom_fields), 0)

        user = TestBridgeUser.users.replace_uid(
            "oldbill", "bill", no_custom_fields=False)
        self.verify_uid(user)
        self.assertEqual(len(user.custom_fields), 1)
        cus_field = user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_field.value,
                         "FBB38FE46A7C11D5A4AE0004AC494FFE")

    def test_restore_user(self):
        self.assertRaises(DataFailureException,
                          TestBridgeUser.users.restore_user_by_id,
                          195)

        self.assertRaises(DataFailureException,
                          TestBridgeUser.users.restore_user,
                          'javerage')

        user = TestBridgeUser.users.restore_user_by_id(
            17637, include_manager=False, no_custom_fields=True)
        self.verify_uid(user)
        self.assertEqual(len(user.custom_fields), 0)

        user = TestBridgeUser.users.restore_user_by_id(
            17637, include_manager=False)
        self.verify_uid(user)
        self.assertEqual(len(user.custom_fields), 1)
        cus_fie = user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_fie.value,
                         "FBB38FE46A7C11D5A4AE0004AC494FFE")

        user = TestBridgeUser.users.restore_user_by_id(17637)
        self.verify_uid(user)
        self.assertTrue(user.has_manager())
        cus_fie = user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_fie.value,
                         "FBB38FE46A7C11D5A4AE0004AC494FFE")

        user = TestBridgeUser.users.restore_user(
            "bill", include_manager=False, no_custom_fields=True)
        self.verify_uid(user)
        self.assertFalse(user.has_custom_field())

        user = TestBridgeUser.users.restore_user(
            "bill", include_manager=False)
        self.verify_uid(user)
        cus_fie = user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_fie.value,
                         "FBB38FE46A7C11D5A4AE0004AC494FFE")

        user = TestBridgeUser.users.restore_user("bill")
        self.verify_uid(user)
        self.assertTrue(user.has_manager())
        cus_fie = user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_fie.value,
                         "FBB38FE46A7C11D5A4AE0004AC494FFE")

    def test_update_user(self):
        orig_user = TestBridgeUser.users.get_user_by_id(17637)
        upded_user = TestBridgeUser.users.update_user(orig_user,
                                                      no_custom_fields=False)
        self.verify_bill(upded_user)
        cus_field = upded_user.get_custom_field(BridgeCustomField.REGID_NAME)
        self.assertEqual(cus_field.value,
                         "FBB38FE46A7C11D5A4AE0004AC494FFE")
        self.assertFalse(upded_user.is_deleted())
        self.assertEqual(str(upded_user.updated_at),
                         '2016-09-08 13:58:20.635000-07:00')

        user = BridgeUser(netid='bill',
                          first_name='Bill Average',
                          last_name='Teacher',
                          email='bill@u.washington.edu',
                          full_name='Bill Average Teacher')
        upded_user = TestBridgeUser.users.update_user(user)
        self.verify_bill(upded_user)
        self.assertIsNone(user.get_custom_field(BridgeCustomField.REGID_NAME))

        orig_user = TestBridgeUser.users.get_user('javerage')
        self.assertRaises(DataFailureException,
                          TestBridgeUser.users.update_user, orig_user)

    def verify_uid(self, user):
        self.assertEqual(user.bridge_id, 17637)
        self.assertEqual(user.get_uid(), "bill@uw.edu")
