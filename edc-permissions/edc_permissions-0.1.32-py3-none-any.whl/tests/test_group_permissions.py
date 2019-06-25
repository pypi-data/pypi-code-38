from django.test import TestCase, tag
from django.contrib.auth.models import Group

from ..groups_updater import GroupsUpdater


class TestGroupPermissions(TestCase):
    def test_groups(self):
        grp = GroupsUpdater()
        self.assertGreater(Group.objects.filter(name__in=grp.group_names).count(), 0)
