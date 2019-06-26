# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
App Menus
"""

from __future__ import unicode_literals, absolute_import

from rattail.core import Object
from rattail.util import import_module_path


class MenuGroup(Object):
    title = None
    items = None
    is_link = False


class MenuItem(Object):
    title = None
    url = None
    target = None
    is_link = True
    is_sep = False


class MenuSeparator(object):
    is_sep = True


def make_simple_menus(request):
    """
    Build the main menu list for the app.
    """
    menus_module = import_module_path(
        request.rattail_config.require('tailbone', 'menus'))

    if not hasattr(menus_module, 'simple_menus') or not callable(menus_module.simple_menus):
        raise RuntimeError("module does not have a simple_menus() callable: {}".format(menus_module))

    # collect "simple" menus definition, but must refine that somewhat to
    # produce our final menus
    raw_menus = menus_module.simple_menus(request)
    final_menus = []
    for topitem in raw_menus:

        if topitem.get('type') == 'link':
            final_menus.append(
                MenuItem(title=topitem['title'],
                         url=topitem['url'],
                         target=topitem.get('target')))

        else: # assuming 'menu' type

            # figure out which ones the user has permission to access
            allowed = []
            for item in topitem['items']:

                if item.get('type') == 'sep':
                    allowed.append(item)

                if item.get('perm'):
                    if request.has_perm(item['perm']):
                        allowed.append(item)
                else:
                    allowed.append(item)

            if allowed:

                # user must have access to something; construct items for the menu
                menu_items = []
                for item in allowed:

                    # separator
                    if item.get('type') == 'sep':
                        if menu_items and not menu_items[-1].is_sep:
                            menu_items.append(MenuSeparator())

                    # menu item
                    else:
                        menu_items.append(
                            MenuItem(title=item['title'],
                                     url=item['url'],
                                     target=item.get('target')))

                # remove final separator if present
                if menu_items and menu_items[-1].is_sep:
                    menu_items.pop()

                # only add if we wound up with something
                if menu_items:
                    final_menus.append(
                        MenuGroup(title=topitem['title'], items=menu_items))

    return final_menus
