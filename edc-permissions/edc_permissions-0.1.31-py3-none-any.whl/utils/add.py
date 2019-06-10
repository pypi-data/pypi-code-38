from django.contrib.auth.models import Permission

from ..constants import NAVBAR_CODENAMES, DASHBOARD_CODENAMES
from .generic import (
    add_permissions_to_group_by_app_label,
    add_permissions_to_group_by_tuples,
    make_view_only_app_label,
    make_view_only_model,
    verify_codename_exists,
)


def add_edc_action_permissions(group, view_only=None, allow_delete=None):
    permissions = Permission.objects.filter(content_type__app_label="edc_action_item")
    for permission in permissions:
        group.permissions.add(permission)

    if view_only:
        make_view_only_model(group, "edc_action_item.actiontype")
    if not allow_delete:
        permissions = Permission.objects.filter(
            content_type__app_label="edc_action_item", codename__startswith="delete"
        )
        for permission in permissions:
            group.permissions.remove(permission)


def add_edc_appointment_permissions(group):
    for permission in Permission.objects.filter(
        content_type__app_label="edc_appointment"
    ):
        group.permissions.add(permission)
    permission = Permission.objects.get(
        content_type__app_label="edc_appointment", codename="delete_appointment"
    )
    group.permissions.remove(permission)


def add_edc_offstudy_permissions(group):
    for permission in Permission.objects.filter(content_type__app_label="edc_offstudy"):
        group.permissions.add(permission)


def add_review_listboard_permissions(group, codenames=None):
    codenames = codenames or [
        "edc_dashboard.view_lab_requisition_listboard",
        "edc_dashboard.view_subject_review_listboard",
    ]

    permissions = []
    for codename in codenames:
        permissions.append(verify_codename_exists(codename))

    for permission in permissions:
        group.permissions.add(permission)


def add_edc_navbar_permissions(group=None):
    codename_tpls = NAVBAR_CODENAMES.get(group.name, [])
    add_permissions_to_group_by_tuples(group, codename_tpls)


def add_edc_dashboard_permissions(group=None):
    codename_tpls = DASHBOARD_CODENAMES.get(group.name, [])
    add_permissions_to_group_by_tuples(group, codename_tpls)


def add_edc_reference_permissions(group=None):
    add_permissions_to_group_by_app_label(group, "edc_reference")
    make_view_only_app_label(group, "edc_reference")
