from django.contrib.auth.models import Group

from ..constants import NAVBAR_CODENAMES, DASHBOARD_CODENAMES
from .generic import create_permissions_from_tuples, remove_permissions_by_codenames


def create_edc_dashboard_permissions(extra_codename_tpls=None):
    model = "edc_dashboard.dashboard"
    for _, codename_tpls in DASHBOARD_CODENAMES.items():
        create_permissions_from_tuples(model, codename_tpls)
    create_permissions_from_tuples(model, extra_codename_tpls)
    for group in Group.objects.all():
        remove_permissions_by_codenames(
            group=group,
            codenames=[
                "edc_dashboard.add_dashboard",
                "edc_dashboard.change_dashboard",
                "edc_dashboard.delete_dashboard",
                "edc_dashboard.view_dashboard",
            ],
        )


def create_edc_navbar_permissions(extra_codename_tpls=None):
    model = "edc_navbar.navbar"
    for _, codename_tpls in NAVBAR_CODENAMES.items():
        create_permissions_from_tuples(model, codename_tpls)
    create_permissions_from_tuples(model, extra_codename_tpls)
    for group in Group.objects.all():
        remove_permissions_by_codenames(
            group=group,
            codenames=[
                "edc_navbar.add_navbar",
                "edc_navbar.change_navbar",
                "edc_navbar.delete_navbar",
                "edc_navbar.view_navbar",
            ],
        )
