# -*- coding: utf-8 -*-
from collective.contentgroups import testing
from plone import api
from Products.PlonePAS.plugins.ufactory import PloneUser

import unittest


class BehaviorTestCase(unittest.TestCase):
    """Test our behavior.

    We test some minor things from the IGroup adapter / Group provider anyway.
    You won't often directly use this.
    """

    layer = testing.COLLECTIVE_CONTENT_GROUPS_CREATED_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]

    def test_igroup(self):
        from collective.contentgroups.behavior import IGroup
        from collective.contentgroups.utils import list_users

        group = self.portal.content1
        adapted = IGroup(group)
        self.assertEqual(
            group.users, "standard_sub_of_content\ncontent1-corey\ngeneral"
        )
        # The getter returns what we have (not a sorted list like at some point).
        self.assertEqual(
            adapted.users, "standard_sub_of_content\ncontent1-corey\ngeneral"
        )
        # Set it to the same, but with the sorted list as value.
        adapted.users = list_users(adapted.users)
        self.assertEqual(
            group.users, "content1-corey\ngeneral\nstandard_sub_of_content"
        )
        # Set to single string.
        adapted.users = "pete"
        self.assertEqual(group.users, "pete")
        self.assertEqual(adapted.users, "pete")
        # Set to stupid string
        adapted.users = "\n\tfoobar   \n\n\n\r\n  ello  \n\n"
        self.assertEqual(group.users, "ello\nfoobar")
        self.assertEqual(adapted.users, "ello\nfoobar")
        # Set to integer, to see that we do not break easily.
        adapted.users = 42
        self.assertEqual(group.users, "42")
        self.assertEqual(adapted.users, "42")


class IntegrationTestCase(unittest.TestCase):
    """Test how our plugin is integrated in PAS."""

    layer = testing.COLLECTIVE_CONTENT_GROUPS_CREATED_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.pas = self.portal.acl_users

    def _makeUser(self, userid="general"):
        # Create a transient/temporary user (much like our GroupAdapter is transient/temporary).
        # Note that the "general" user is a member of all our extra groups.
        return PloneUser(userid)

    def test_searchGroups(self):
        # PAS.searchGroups looks for IGroupEnumerationPlugin plugins
        # and calls enumerateGroups on them with some keywords.
        # Without keyword arguments, we expect our groups plus Administrators, etc.
        groups = self.pas.searchGroups()
        self.assertGreaterEqual(len(groups), 10)
        ids = [g["groupid"] for g in groups]
        self.assertIn("Administrators", ids)
        self.assertIn("casual", ids)
        self.assertIn("content1", ids)
        # Strangely, max_results returns one result more than asked.
        self.assertEqual(len(self.pas.searchGroups(max_results=5)), 6)
        # Searching for name returns anything with content in the title,
        # so also our sub groups with 'Sub Content' in the title.
        self.assertEqual(len(self.pas.searchGroups(name="content")), 6)
        self.assertEqual(len(self.pas.searchGroups(name="sub content")), 3)
        # id is pickier.  Well, PlonePAS source_groups finds one that contains 'content'.
        content = self.pas.searchGroups(id="content")
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]["id"], "standard_sub_of_content")
        self.assertEqual(content[0]["pluginid"], "source_groups")
        self.assertEqual(len(self.pas.searchGroups(id="content1")), 1)
        self.assertEqual(len(self.pas.searchGroups(id="Content1")), 0)
        # We can have multiple ids though:
        self.assertEqual(len(self.pas.searchGroups(id=("content1", "sub2a"))), 2)
        # sort_by and max_results are not passed from PAS to the plugins,
        # but that seems wrong to me.  Let's test it anyway.
        groups = self.pas.searchGroups(name="content", sort_by="title", max_results=2)
        self.assertEqual(len(groups), 3)
        ids = [g["groupid"] for g in groups]
        self.assertListEqual(ids, ["sub2a", "sub2b", "content1"])

    def test_getGroupsForPrincipal(self):
        # PAS._getGroupsForPrincipal looks for IGroupsPlugin plugins
        # and calls_getGroupsForPrincipal on them with principal and request.
        general = self._makeUser()
        groups = self.pas._getGroupsForPrincipal(general)
        # Apparently the auto_group AuthenticatedUsers is always in there.
        self.assertListEqual(
            sorted(groups),
            [
                "AuthenticatedUsers",
                "casual",
                "content1",
                "content2",
                "content_sub_of_standard",
                "standard_sub_of_content",
                "sub2a",
                "sub2b",
                "subcasual",
            ],
        )
        self.assertListEqual(
            sorted(self.pas._getGroupsForPrincipal(self._makeUser("casual-ann"))),
            ["AuthenticatedUsers", "casual"],
        )
        self.assertListEqual(
            sorted(self.pas._getGroupsForPrincipal(self._makeUser("content1-corey"))),
            ["AuthenticatedUsers", "content1"],
        )
        # We have one user who is member of all sub groups.  Do the parent groups get reported properly?
        self.assertListEqual(
            sorted(self.pas._getGroupsForPrincipal(self._makeUser("sub"))),
            [
                "AuthenticatedUsers",
                "casual",
                "content1",
                "content2",
                "content_sub_of_standard",
                "standard_sub_of_content",
                "sub2a",
                "sub2b",
                "subcasual",
            ],
        )

        # Bert is member of subcasual, which is sub group of casual.  Both non-content.
        self.assertListEqual(
            sorted(self.pas._getGroupsForPrincipal(self._makeUser("subcasual-bert"))),
            ["AuthenticatedUsers", "casual", "subcasual"],
        )
        # Does this work for our content groups too?
        # Eddy is a member of sub2a, and that is a sub group of content2.
        self.assertListEqual(
            sorted(self.pas._getGroupsForPrincipal(self._makeUser("sub2a-eddy"))),
            ["AuthenticatedUsers", "content2", "sub2a"],
        )

    def test_getGroupMembers_and_getGroupMembers(self):
        # Do PloneGroup and our GroupAdapter handle these methods the same way?
        standard = self.pas.getGroupById("casual")
        content1 = self.pas.getGroupById("content1")
        content2 = self.pas.getGroupById("content2")
        self.assertEqual(
            sorted([x.id for x in standard.getGroupMembers()]),
            ["casual-ann", "content_sub_of_standard", "general", "subcasual"],
        )
        # Our group members are always sorted.
        self.assertEqual(
            [x.id for x in content1.getGroupMembers()],
            ["content1-corey", "general", "standard_sub_of_content"],
        )
        self.assertEqual(
            [x.id for x in content2.getGroupMembers()],
            ["content2-donna", "general", "sub2a", "sub2b"],
        )
        # According to the documentation the getAllGroupMembers also returns users from sub groups,
        # but in practice this does not happen.
        self.assertEqual(
            sorted([x.id for x in standard.getGroupMembers()]),
            sorted([x.id for x in standard.getAllGroupMembers()]),
        )
        self.assertEqual(
            [x.id for x in content1.getGroupMembers()],
            [x.id for x in content1.getAllGroupMembers()],
        )
        self.assertEqual(
            [x.id for x in content2.getGroupMembers()],
            [x.id for x in content2.getAllGroupMembers()],
        )

    def test_getGroupMemberIds_and_getAllGroupMemberIds(self):
        # Do PloneGroup and our GroupAdapter handle these methods the same way?
        standard = self.pas.getGroupById("casual")
        content1 = self.pas.getGroupById("content1")
        content2 = self.pas.getGroupById("content2")
        self.assertEqual(
            sorted(standard.getGroupMemberIds()),
            ["casual-ann", "content_sub_of_standard", "general", "subcasual"],
        )
        # Our group member ids are always sorted.
        self.assertEqual(
            content1.getGroupMemberIds(),
            ["content1-corey", "general", "standard_sub_of_content"],
        )
        self.assertEqual(
            content2.getGroupMemberIds(),
            ["content2-donna", "general", "sub2a", "sub2b"],
        )
        # According to the documentation the getAllGroupMembers also returns users from sub groups,
        # but in practice this does not happen.
        self.assertEqual(
            sorted(standard.getGroupMemberIds()),
            sorted(standard.getAllGroupMemberIds()),
        )
        self.assertEqual(content1.getGroupMemberIds(), content1.getAllGroupMemberIds())
        self.assertEqual(content2.getGroupMemberIds(), content2.getAllGroupMemberIds())

    def test_duplicate_group_id_for_standard_groups_and_users(self):
        # You shouldn't be able to add a Group with an id that already exists.
        # While adding standard groups or users, this is already checked.
        # Note that there are similar tests in test_functional.py,
        # where we try to create content.
        len_users = len(api.user.get_users())
        self.assertGreaterEqual(len_users, 9)
        with self.assertRaises(ValueError):
            api.user.create(email="x@example.org", username="content1")
        self.assertEqual(len(api.user.get_users()), len_users)
        # Check our logic: adding a unique user is allowed
        api.user.create(email="unique@example.org", username="unique")
        len_users += 1
        self.assertEqual(len(api.user.get_users()), len_users)

        # Strangely, creating a group with the same name silently fails,
        # but gets you the current group.
        len_groups = len(api.group.get_groups())
        self.assertGreaterEqual(len_groups, 9)
        api.group.create(groupname="casual")
        api.group.create(groupname="content1")
        # Check that no groups have been added:
        self.assertEqual(len(api.group.get_groups()), len_groups)
