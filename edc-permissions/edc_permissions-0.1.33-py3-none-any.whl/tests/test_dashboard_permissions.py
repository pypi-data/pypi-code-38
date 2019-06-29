from django.apps import apps as django_apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.test import TestCase, tag

from ..constants.dashboard_codenames import (
    LAB_DASHBOARD_CODENAMES,
    REVIEW_DASHBOARD_CODENAMES,
    CLINIC_DASHBOARD_CODENAMES,
)
from ..groups_updater import GroupsUpdater as DefaultGroupsUpdater
from ..utils import (
    INVALID_APP_LABEL,
    PermissionsCreatorError,
    as_codenames_from_tuples,
    verify_codename_exists,
)
from ..utils import create_edc_dashboard_permissions


class TestEdcDashboardPermissions(TestCase):
    def setUp(self):
        DefaultGroupsUpdater()

    def test_dashboard_codenames(self):

        create_edc_dashboard_permissions()

        codenames = as_codenames_from_tuples(LAB_DASHBOARD_CODENAMES)
        self.assertGreater(
            Permission.objects.filter(
                codename__in=[c.split(".")[1] for c in codenames]
            ).count(),
            0,
        )

        codenames = as_codenames_from_tuples(REVIEW_DASHBOARD_CODENAMES)
        self.assertGreater(
            Permission.objects.filter(
                codename__in=[c.split(".")[1] for c in codenames]
            ).count(),
            0,
        )

        codenames = as_codenames_from_tuples(CLINIC_DASHBOARD_CODENAMES)
        self.assertGreater(
            Permission.objects.filter(
                codename__in=[c.split(".")[1] for c in codenames]
            ).count(),
            0,
        )

        model_cls = django_apps.get_model("edc_dashboard.dashboard")
        ct = ContentType.objects.get_for_model(model_cls)
        self.assertGreater(Permission.objects.filter(content_type=ct).count(), 0)
        for perm in Permission.objects.filter(content_type=ct):
            codename = f"{perm.content_type.app_label}.{perm.codename}"
            verify_codename_exists(codename=codename)

    def test_adds_extra_dashboard_codenames(self):
        class GroupsUpdater(DefaultGroupsUpdater):
            extra_group_names = ["ERIK"]

        GroupsUpdater()

        extra_codenames = [("edc_dashboard.view_erik", "View Erik")]

        create_edc_dashboard_permissions(extra_codename_tpls=extra_codenames)

        codenames = as_codenames_from_tuples(extra_codenames)
        self.assertEqual(
            Permission.objects.filter(
                codename__in=[c.split(".")[1] for c in codenames]
            ).count(),
            1,
        )

    def test_detects_bad_app_label(self):
        class GroupsUpdater(DefaultGroupsUpdater):
            extra_group_names = ["ERIK"]

        GroupsUpdater()

        extra_codenames = [
            ("blah.view_subject_review_listboard", "Can view Subject Review Listboard")
        ]
        with self.assertRaises(PermissionsCreatorError) as cm:
            create_edc_dashboard_permissions(extra_codename_tpls=extra_codenames)
        self.assertEqual(cm.exception.code, INVALID_APP_LABEL)
