from django.core.urlresolvers import reverse
from menu import Menu, MenuItem

sharing_children = (
    MenuItem("Identity", reverse("admin:core_oaipmh_provider_app_identity"), icon="gear"),
    MenuItem("Metadata Formats",
             reverse("admin:core_oaipmh_provider_app_metadata_formats"), icon="book"),
    MenuItem("Sets", reverse("admin:core_oaipmh_provider_app_sets"), icon="reorder"),
)

Menu.add_item(
    "admin", MenuItem("OAI-PMH PROVIDER", None, children=sharing_children)
)
