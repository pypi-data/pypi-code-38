""" Add Explore Example in main menu
"""

from django.core.urlresolvers import reverse
from menu import Menu, MenuItem
from core_explore_example_app.settings import EXPLORE_EXAMPLE_MENU_NAME

# FIXME: CHECK AUTHENTICATION !
Menu.add_item(
    "main", MenuItem(EXPLORE_EXAMPLE_MENU_NAME, reverse("core_explore_example_index"))
)
