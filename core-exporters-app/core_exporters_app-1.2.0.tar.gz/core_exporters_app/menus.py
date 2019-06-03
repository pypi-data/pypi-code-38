""" Exporter app menu
"""
from django.core.urlresolvers import reverse
from menu import Menu, MenuItem


federated_children = (
    MenuItem("Exporter List", reverse("admin:core_exporters_app_exporters"), icon="list"),
)

Menu.add_item(
    "admin", MenuItem("EXPORTERS", None, children=federated_children)
)
