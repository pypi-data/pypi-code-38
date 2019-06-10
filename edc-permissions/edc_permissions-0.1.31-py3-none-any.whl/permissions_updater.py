import sys

from .groups_updater import GroupsUpdater
from .utils import (
    create_edc_dashboard_permissions,
    create_edc_navbar_permissions,
    update_account_manager_group_permissions,
    update_administration_group_permissions,
    update_auditor_group_permissions,
    update_clinic_group_permissions,
    update_data_manager_group_permissions,
    update_data_query_group_permissions,
    update_everyone_group_permissions,
    update_export_group_permissions,
    update_lab_group_permissions,
    update_lab_view_group_permissions,
    update_pharmacy_group_permissions,
    update_pii_group_permissions,
    update_pii_view_group_permissions,
)


class PermissionsUpdater:
    def __init__(
        self, extra_pii_models=None, extra_updaters=None, extra_group_names=None
    ):

        GroupsUpdater(extra_group_names=extra_group_names)

        create_edc_dashboard_permissions()
        create_edc_navbar_permissions()

        sys.stdout.write("  * account manager\n")
        update_account_manager_group_permissions()
        sys.stdout.write("  * administration\n")
        update_administration_group_permissions()
        sys.stdout.write("  * auditor manager\n")
        update_auditor_group_permissions()
        sys.stdout.write("  * clinic\n")
        update_clinic_group_permissions()
        sys.stdout.write("  * data_manager\n")
        update_data_manager_group_permissions()
        sys.stdout.write("  * data_query\n")
        update_data_query_group_permissions()
        sys.stdout.write("  * everyone\n")
        update_everyone_group_permissions()
        sys.stdout.write("  * export\n")
        update_export_group_permissions()
        sys.stdout.write("  * lab_group\n")
        update_lab_group_permissions()
        sys.stdout.write("  * lab_view\n")
        update_lab_view_group_permissions()
        sys.stdout.write("  * pharmacy\n")
        update_pharmacy_group_permissions()
        sys.stdout.write("  * pii\n")
        update_pii_group_permissions(extra_pii_models=extra_pii_models)
        sys.stdout.write("  * pii_view\n")
        update_pii_view_group_permissions(extra_pii_models=extra_pii_models)

        sys.stdout.write("  * extras ...\n")
        for updater in extra_updaters or []:
            group_name = updater()
            sys.stdout.write(f"    - {group_name.lower()}\n")
