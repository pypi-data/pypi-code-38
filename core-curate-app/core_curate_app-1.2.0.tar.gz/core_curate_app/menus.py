""" Add Curate in main menu
"""

from django.core.urlresolvers import reverse
from menu import Menu, MenuItem

from core_curate_app.settings import CURATE_MENU_NAME

Menu.add_item(
    "main", MenuItem(CURATE_MENU_NAME, reverse("core_curate_index"))
)
