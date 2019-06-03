from django.core.urlresolvers import reverse
from menu import Menu, MenuItem


Menu.add_item(
    "footer", MenuItem("Privacy policy", reverse("core_website_app_privacy"), weight=1001)
)

Menu.add_item(
    "footer", MenuItem("Terms of use", reverse("core_website_app_terms"), weight=1002)
)

Menu.add_item(
    "footer", MenuItem("Contact", reverse("core_website_app_contact"), icon="envelope", weight=1003)
)

Menu.add_item(
    "footer", MenuItem("Help", reverse("core_website_app_help"), icon="question-circle", weight=1004)
)

# Admin menus for website app
website_children = (
    MenuItem("Privacy Policy", reverse("admin:core_website_app_privacy"), icon="user-secret"),
    MenuItem("Terms of Use", reverse("admin:core_website_app_terms"), icon="file-text-o"),
    MenuItem("Help Page", reverse("admin:core_website_app_help"), icon="question-circle-o"),

    MenuItem("User requests", reverse("admin:core_website_app_user_requests"), icon="user-plus",
             item_count_url="admin:core_website_app_request_count"),
    MenuItem("Contact messages", reverse("admin:core_website_app_contact_messages"), icon="envelope",
             item_count_url="admin:core_website_app_message_count"),
)

Menu.add_item(
    "admin", MenuItem("WEBSITE", None, children=website_children, weight=-10000)
)
