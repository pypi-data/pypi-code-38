from unittest import TestCase
from uw_bridge.models import BridgeUserRole
from uw_bridge.user_roles import UserRoles
from uw_bridge.tests import fdao_bridge_override


@fdao_bridge_override
class TestBridgeUserRoles(TestCase):

    def test_userroles(self):
        cfs = UserRoles()
        self.assertEqual(len(cfs.get_roles()), 5)
        roles = cfs.get_roles()
        self.assertTrue(roles[0].is_account_admin())
        self.assertTrue(roles[1].is_admin())
        self.assertTrue(roles[2].is_author())
        self.assertTrue(roles[3].is_campus_admin())
        self.assertTrue(roles[4].is_it_admin())

        self.assertEqual(cfs.get_role_id(
            BridgeUserRole.ACCOUNT_ADMIN_NAME), "account_admin")
        self.assertEqual(cfs.get_role_id(
            BridgeUserRole.ADMIN_NAME), "admin")
        self.assertEqual(cfs.get_role_id(
            BridgeUserRole.AUTHOR_NAME), "author")
        self.assertEqual(cfs.get_role_id(
            BridgeUserRole.CAMPUS_ADMIN_NAME), "fb412e52")
        self.assertEqual(cfs.get_role_id(
            BridgeUserRole.IT_ADMIN_NAME), "it_admin")

        self.assertEqual(cfs.get_role_name("account_admin"),
                         BridgeUserRole.ACCOUNT_ADMIN_NAME)
        self.assertEqual(cfs.get_role_name("admin"),
                         BridgeUserRole.ADMIN_NAME)
        self.assertEqual(cfs.get_role_name("author"),
                         BridgeUserRole.AUTHOR_NAME)
        self.assertEqual(cfs.get_role_name("fb412e52"),
                         BridgeUserRole.CAMPUS_ADMIN_NAME)
        self.assertEqual(cfs.get_role_name("it_admin"),
                         BridgeUserRole.IT_ADMIN_NAME)

        role = cfs.new_user_role_by_name(BridgeUserRole.ACCOUNT_ADMIN_NAME)
        self.assertTrue(role.is_account_admin())
        self.assertEqual(role.to_json(),
                         {'id': 'account_admin', 'name': 'Account Admin'})
        self.assertIsNotNone(str(role))

        role = cfs.new_user_role_by_name(BridgeUserRole.CAMPUS_ADMIN_NAME)
        self.assertEqual(role.role_id, "fb412e52")

        role = cfs.new_user_role_by_id("author")
        self.assertEqual(role.name, BridgeUserRole.AUTHOR_NAME)
