from django.test import TestCase, tag

from ..utils import (
    create_edc_dashboard_permissions,
    create_edc_navbar_permissions,
    update_account_manager_group_permissions,
    update_administration_group_permissions,
    update_auditor_group_permissions,
    update_clinic_group_permissions,
    update_data_manager_group_permissions,
    update_everyone_group_permissions,
    update_export_group_permissions,
    update_lab_group_permissions,
    update_lab_view_group_permissions,
    update_pharmacy_group_permissions,
    update_pii_group_permissions,
)

from ..groups_updater import GroupsUpdater
from ..utils import compare_codenames_for_group
from ..constants import (
    CLINIC,
    ACCOUNT_MANAGER,
    LAB,
    LAB_VIEW,
    ADMINISTRATION,
    AUDITOR,
    DATA_MANAGER,
    EVERYONE,
    EXPORT,
    PHARMACY,
    PII,
    PII_VIEW,
    DEFAULT_CODENAMES,
)
from ..codenames import (
    account_manager,
    administration,
    auditor,
    clinic,
    data_manager,
    everyone,
    export,
    lab,
    lab_view,
    pharmacy,
    pii,
    pii_view,
)
from ..permissions_updater import PermissionsUpdater


class TestUpdaterMixins(TestCase):
    def setUp(self):
        GroupsUpdater()
        create_edc_dashboard_permissions()
        create_edc_navbar_permissions()

    def test_pii(self):
        update_pii_group_permissions()
        # show_permissions_for_group(group_name=PII)
        compare_codenames_for_group(group_name=PII, expected=pii)
        # show_permissions_for_group(group_name=PII_VIEW)
        compare_codenames_for_group(group_name=PII_VIEW, expected=pii_view)

    def test_pharmacy(self):

        update_pharmacy_group_permissions()
        compare_codenames_for_group(group_name=PHARMACY, expected=pharmacy)

    def test_export(self):
        update_export_group_permissions()
        compare_codenames_for_group(group_name=EXPORT, expected=export)

    def test_everyone(self):
        update_everyone_group_permissions()
        compare_codenames_for_group(group_name=EVERYONE, expected=everyone)

    def test_data_manager(self):
        update_data_manager_group_permissions()
        compare_codenames_for_group(group_name=DATA_MANAGER, expected=data_manager)

    def test_auditors(self):
        update_auditor_group_permissions()
        compare_codenames_for_group(group_name=AUDITOR, expected=auditor)

    def test_administrations(self):
        update_administration_group_permissions()
        compare_codenames_for_group(group_name=ADMINISTRATION, expected=administration)

    def test_account_manager(self):
        update_account_manager_group_permissions()
        compare_codenames_for_group(
            group_name=ACCOUNT_MANAGER, expected=account_manager
        )

    def test_clinic(self):
        update_clinic_group_permissions()
        compare_codenames_for_group(group_name=CLINIC, expected=clinic)

    def test_lab(self):
        update_lab_group_permissions()
        update_lab_view_group_permissions()
        compare_codenames_for_group(group_name=LAB, expected=lab)
        compare_codenames_for_group(group_name=LAB_VIEW, expected=lab_view)

    def test_permissions_updater(self):
        PermissionsUpdater()
        for group_name, expected in DEFAULT_CODENAMES.items():
            compare_codenames_for_group(group_name=group_name, expected=expected)
