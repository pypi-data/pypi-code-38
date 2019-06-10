import sys

from copy import copy
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .constants import (
    DEFAULT_GROUP_NAMES,
    ADMINISTRATION,
    CLINIC,
    LAB,
    PHARMACY,
    AUDITOR,
    PII,
    PII_VIEW,
)
from .utils import remove_duplicates_in_groups

UserModel = get_user_model()


class GroupsUpdater:

    default_group_names = DEFAULT_GROUP_NAMES

    def __init__(self, verbose=None, extra_group_names=None, **kwargs):
        self._group_names = None
        self.extra_group_names = extra_group_names
        self.verbose = verbose
        self.create_or_update_groups()
        self.ensure_users_in_group(ADMINISTRATION, users_by_groups=[CLINIC, LAB])
        self.ensure_users_in_group(PII, users_by_groups=[CLINIC])
        self.ensure_users_in_group(PII_VIEW, users_by_groups=[LAB, PHARMACY])
        self.ensure_users_not_in_group(PII, users_by_groups=[AUDITOR, LAB, PHARMACY])
        self.ensure_users_not_in_group(PII, users_by_groups=[AUDITOR, LAB, PHARMACY])
        self.ensure_users_not_in_group(PII_VIEW, users_by_groups=[AUDITOR])
        remove_duplicates_in_groups(self.group_names)

    @property
    def group_names(self):
        if not self._group_names:
            self._group_names = copy(self.default_group_names or [])
            if self.extra_group_names:
                self._group_names.extend(self.extra_group_names or [])
            self._group_names = list(set(self._group_names))
            self._group_names.sort()
        return self._group_names

    def create_or_update_groups(self):
        """Add/Deletes group model instances to match the
        the given list of group names.
        """

        for name in self.group_names:
            try:
                Group.objects.get(name=name)
            except ObjectDoesNotExist:
                Group.objects.create(name=name)
        Group.objects.exclude(name__in=self.group_names).delete()

        if self.verbose:
            names = [obj.name for obj in Group.objects.all().order_by("name")]
            sys.stdout.write(f"  Groups are: {', '.join(names)}\n")

    def ensure_users_in_group(self, group_name, users_by_groups=None):
        group = Group.objects.get(name=group_name)
        for user in UserModel.objects.filter(groups__name__in=users_by_groups):
            try:
                user.groups.get(name=group.name)
            except ObjectDoesNotExist:
                user.groups.add(group)

    def ensure_users_not_in_group(self, group_name, users_by_groups=None):
        group = Group.objects.get(name=group_name)
        for user in UserModel.objects.filter(groups__name__in=users_by_groups):
            try:
                user.groups.get(name=group.name)
            except ObjectDoesNotExist:
                pass
            else:
                user.groups.remove(group)
