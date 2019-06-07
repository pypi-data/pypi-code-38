# -*- coding: utf-8 -*-
from collective.contentgroups import testing
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import transaction
import unittest


class FunctionalTestCase(unittest.TestCase):
    """Test how our plugin functions in PAS.

    This uses a functional test layer, so we can do commits.
    """

    layer = testing.COLLECTIVE_CONTENT_GROUPS_CREATED_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.pas = self.portal.acl_users

    def test_duplicate_group_id_for_content_groups(self):
        # You shouldn't be able to add a Group with an id that already exists.
        # Or rename one.
        # Note that there are similar tests in test_integration.py,
        # but those do not try to create content.
        setRoles(portal=self.portal, userId=TEST_USER_ID, roles=["Manager"])
        len_groups = len(api.group.get_groups())
        # commit until this point
        transaction.commit()
        # This should be checked for *all* groups, not just content groups.
        # So this should fail:
        with self.assertRaises(api.exc.InvalidParameterError):
            api.content.create(
                container=self.portal,
                type="Group",
                id="Administrators",
                title="Administrators",
            )
        # Strangely, the group is created anyway:
        self.assertEqual(len(api.group.get_groups()), len_groups + 1)
        # This seems a peculiarity of the tests.  In practice, no group is created.
        # So we manually abort the transaction, which we can do in this functional test.
        transaction.abort()
        self.assertEqual(len(api.group.get_groups()), len_groups)

        # Let's test in different folders so that we don't have interference from a group with same name
        # that is found via acquisition.
        api.content.create(
            container=self.portal,
            type="Container",
            id="container1",
            title="Container 1",
        )
        api.content.create(
            container=self.portal.container1, type="Group", id="blup", title="Blup"
        )
        len_groups += 1
        self.assertEqual(len(api.group.get_groups()), len_groups)
        # Try to add group with the same id in a different folder.
        api.content.create(
            container=self.portal,
            type="Container",
            id="container2",
            title="Container 2",
        )
        transaction.commit()
        with self.assertRaises(api.exc.InvalidParameterError):
            api.content.create(
                container=self.portal.container2, type="Group", id="blup", title="Blup"
            )
        # Strangely, like before, the group is created anyway:
        self.assertEqual(len(api.group.get_groups()), len_groups + 1)
        # This seems a peculiarity of the tests.  In practice, no group is created.
        # So we manually abort the transaction, which we can do in this functional test.
        transaction.abort()
        self.assertEqual(len(api.group.get_groups()), len_groups)

        # Now try renaming a content group.
        with self.assertRaises(ValueError):
            api.content.move(source=self.portal.content1, id="blup")
        self.assertEqual(len(api.group.get_groups()), len_groups)
        # Similar problem as before, now the rename seems to have worked:
        self.assertIsNone(api.group.get(groupname="content1"))
        transaction.abort()
        self.assertTrue(api.group.get(groupname="content1"))

        # A move, keeping the same name, is allowed.
        api.content.move(source=self.portal.content1, target=self.portal.container1)
        self.assertEqual(len(api.group.get_groups()), len_groups)
        self.assertTrue(api.group.get(groupname="content1"))
