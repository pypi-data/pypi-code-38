from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

from ..constants import (
    ACCOUNT_MANAGER,
    ADMINISTRATION,
    AUDITOR,
    CLINIC,
    DATA_MANAGER,
    DATA_QUERY,
    EVERYONE,
    EXPORT,
    LAB,
    LAB_VIEW,
    PHARMACY,
)
from ..utils import (
    make_view_only_group,
    make_view_only_model,
    make_view_only_app_label,
    add_permissions_to_group_by_app_label,
    remove_historical_group_permissions,
    add_permissions_to_group_by_codenames,
    add_edc_action_permissions,
    add_edc_appointment_permissions,
    add_edc_offstudy_permissions,
    add_edc_dashboard_permissions,
    add_edc_navbar_permissions,
    add_edc_reference_permissions,
    remove_permissions_from_model_by_action,
)


def update_account_manager_group_permissions(extra_codenames=None):
    group_name = ACCOUNT_MANAGER
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    for app_label in ["auth", "edc_auth", "edc_notification"]:
        add_permissions_to_group_by_app_label(group=group, app_label=app_label)
    add_permissions_to_group_by_codenames(group, extra_codenames)


def update_administration_group_permissions(extra_codenames=None):
    group_name = ADMINISTRATION
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_edc_navbar_permissions(group=group)
    add_edc_dashboard_permissions(group)
    add_permissions_to_group_by_codenames(group, extra_codenames)


def update_auditor_group_permissions(
    extra_auditor_app_labels=None, extra_codenames=None
):
    default_auditor_app_labels = ["edc_lab", "edc_offstudy"]
    group_name = AUDITOR
    group = Group.objects.get(name=group_name)
    group.permissions.clear()

    auditor_app_labels = default_auditor_app_labels
    if extra_auditor_app_labels:
        auditor_app_labels.extend(extra_auditor_app_labels)
    auditor_app_labels = list(set(auditor_app_labels))
    auditor_app_labels.sort()

    for app_label in auditor_app_labels:
        add_permissions_to_group_by_app_label(group, app_label)

    add_edc_action_permissions(group, view_only=True)
    add_edc_appointment_permissions(group)
    add_edc_offstudy_permissions(group)
    add_edc_dashboard_permissions(group)
    add_edc_navbar_permissions(group=group)

    add_permissions_to_group_by_codenames(group, extra_codenames)

    remove_historical_group_permissions(group)

    make_view_only_group(group)


def update_clinic_group_permissions(extra_codenames=None):
    group_name = CLINIC
    group = Group.objects.get(name=group_name)
    group.permissions.clear()

    add_edc_appointment_permissions(group)
    add_edc_offstudy_permissions(group)
    add_edc_action_permissions(group, view_only=True, allow_delete=True)
    add_edc_dashboard_permissions(group)
    add_edc_navbar_permissions(group=group)
    add_edc_reference_permissions(group=group)

    add_permissions_to_group_by_codenames(group, extra_codenames)

    remove_historical_group_permissions(group)


def update_data_manager_group_permissions(extra_codenames=None):
    group_name = DATA_MANAGER
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_permissions_to_group_by_app_label(
        group=group, app_label="edc_metadata")
    add_permissions_to_group_by_app_label(
        group=group, app_label="edc_data_manager")
    add_edc_navbar_permissions(group=group)
    make_view_only_model(group=group, model="edc_data_manager.queryuser")
    make_view_only_model(
        group=group, model="edc_data_manager.datamanageruser")
    make_view_only_model(group=group, model="edc_data_manager.datadictionary")
    make_view_only_model(
        group=group, model="edc_data_manager.queryvisitschedule")
    add_permissions_to_group_by_codenames(group, extra_codenames)
    remove_historical_group_permissions(group=group)


def update_data_query_group_permissions(extra_codenames=None):
    group_name = DATA_QUERY
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_edc_navbar_permissions(group=group)

    add_permissions_to_group_by_app_label(
        group=group, app_label="edc_metadata")
    add_permissions_to_group_by_app_label(
        group=group, app_label="edc_data_manager")

    remove_permissions_from_model_by_action(
        group=group, model="edc_data_manager.dataquery", actions=["add", "delete"])

    make_view_only_app_label(group=group, app_label="edc_metadata")
    make_view_only_model(group=group, model="edc_data_manager.queryuser")
    make_view_only_model(group=group, model="edc_data_manager.datamanageruser")
    make_view_only_model(group=group, model="edc_data_manager.datadictionary")
    make_view_only_model(
        group=group, model="edc_data_manager.queryvisitschedule")

    add_permissions_to_group_by_codenames(group, extra_codenames)
    remove_historical_group_permissions(group=group)


def update_everyone_group_permissions(extra_codenames=None):
    group_name = EVERYONE
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    # add model permissions
    for permission in Permission.objects.filter(
        content_type__app_label="edc_auth",
        content_type__model="userprofile",
        codename__in=["view_userprofile"],
    ):
        group.permissions.add(permission)
    for permission in Permission.objects.filter(
        content_type__app_label="auth",
        content_type__model__in=["user", "group", "permission"],
        codename__startswith="view",
    ):
        group.permissions.add(permission)
    for permission in Permission.objects.filter(
        content_type__app_label="sites",
        content_type__model="site",
        codename__startswith="view",
    ):
        group.permissions.add(permission)
    for permission in Permission.objects.filter(
        content_type__app_label="admin", codename__startswith="view"
    ):
        group.permissions.add(permission)
    # add all active users to group
    User = get_user_model()
    for user in User.objects.filter(is_active=True, is_staff=True):
        user.groups.add(group)

    add_edc_navbar_permissions(group=group)
    add_edc_dashboard_permissions(group=group)
    add_permissions_to_group_by_codenames(group, extra_codenames)


def update_export_group_permissions(extra_codenames=None):
    group_name = EXPORT
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_permissions_to_group_by_app_label(group=group, app_label="edc_export")
    # self.add_dashboard_permissions(group, dashboard_category=group_name)
    add_edc_navbar_permissions(group=group)
    add_permissions_to_group_by_codenames(group, extra_codenames)
    remove_historical_group_permissions(group)


def update_lab_group_permissions(extra_codenames=None):
    group_name = LAB
    group = Group.objects.get(name=group_name)
    group.permissions.clear()

    add_permissions_to_group_by_app_label(group, "edc_lab")
    add_edc_dashboard_permissions(group)
    add_edc_navbar_permissions(group=group)
    add_permissions_to_group_by_codenames(group, extra_codenames)

    remove_historical_group_permissions(group)


def update_lab_view_group_permissions(extra_codenames=None):
    group_name = LAB_VIEW
    group = Group.objects.get(name=group_name)
    group.permissions.clear()

    add_permissions_to_group_by_app_label(group, "edc_lab")
    add_edc_dashboard_permissions(group)
    add_edc_navbar_permissions(group=group)
    add_permissions_to_group_by_codenames(group, extra_codenames)

    remove_historical_group_permissions(group)

    make_view_only_group(group)


def update_pharmacy_group_permissions(extra_codenames=None):
    group_name = PHARMACY
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_permissions_to_group_by_app_label(group, "edc_pharmacy")
    add_edc_dashboard_permissions(group)
    add_edc_navbar_permissions(group=group)
    add_permissions_to_group_by_codenames(group, extra_codenames)
    remove_historical_group_permissions(group)
