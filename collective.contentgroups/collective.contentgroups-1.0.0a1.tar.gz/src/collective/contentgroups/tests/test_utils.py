# -*- coding: utf-8 -*-
import unittest


class DummyGroup(object):
    def __init__(self, id, users=""):
        self.id = id
        self.users = users


class UtilsUnitTestCase(unittest.TestCase):
    """Test our utility functions."""

    def _makeGroup(self, groupid="group1", users=""):
        return DummyGroup(groupid, users=users)

    def test_list_users(self):
        from collective.contentgroups.utils import list_users

        self.assertListEqual(list_users(None), [])
        self.assertListEqual(list_users(self._makeGroup()), [])
        self.assertListEqual(list_users(self._makeGroup(users="joe")), ["joe"])
        self.assertListEqual(list_users(self._makeGroup(users="   joe \n   ")), ["joe"])
        self.assertListEqual(
            list_users(self._makeGroup(users="joe\njane")), ["jane", "joe"]
        )
        self.assertListEqual(
            list_users(self._makeGroup(users="\n  \r\n\tjoe\t\n\rjane\n")),
            ["jane", "joe"],
        )
        # We support listing (and filtering and sorting) from a simple string too.
        self.assertListEqual(list_users(""), [])
        self.assertListEqual(list_users("pete"), ["pete"])
        self.assertListEqual(list_users("\n  \r\n\tjoe\t\n\rjane\n"), ["jane", "joe"])
