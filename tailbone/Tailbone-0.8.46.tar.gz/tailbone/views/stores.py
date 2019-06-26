# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Store Views
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa

from rattail.db import model

import colander

from tailbone import grids
from tailbone.views import MasterView


class StoresView(MasterView):
    """
    Master view for the Store class.
    """
    model_class = model.Store
    has_versions = True

    grid_columns = [
        'id',
        'name',
        'phone',
        'email',
    ]

    labels = {
        'id':           "ID",
        'phone':        "Phone Number",
        'email':        "Email Address",
    }

    def configure_grid(self, g):
        super(StoresView, self).configure_grid(g)

        g.set_joiner('email', lambda q: q.outerjoin(model.StoreEmailAddress, sa.and_(
            model.StoreEmailAddress.parent_uuid == model.Store.uuid,
            model.StoreEmailAddress.preference == 1)))
        g.set_joiner('phone', lambda q: q.outerjoin(model.StorePhoneNumber, sa.and_(
            model.StorePhoneNumber.parent_uuid == model.Store.uuid,
            model.StorePhoneNumber.preference == 1)))

        g.set_filter('phone', model.StorePhoneNumber.number,
                     factory=grids.filters.AlchemyPhoneNumberFilter)
        g.filters['email'] = g.make_filter('email', model.StoreEmailAddress.address)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'

        g.set_sorter('phone', model.StorePhoneNumber.number)
        g.set_sorter('email', model.StoreEmailAddress.address)
        g.set_sort_defaults('id')

        g.set_link('id')
        g.set_link('name')

    def configure_form(self, f):
        super(StoresView, self).configure_form(f)

        f.remove_field('employees')
        f.remove_field('phones')
        f.remove_field('emails')

        if self.creating:
            f.remove_field('phone')
            f.remove_field('email')
        else:
            f.set_readonly('phone')
            f.set_readonly('email')

    def get_version_child_classes(self):
        return [
            (model.StorePhoneNumber, 'parent_uuid'),
            (model.StoreEmailAddress, 'parent_uuid'),
        ]


def includeme(config):
    StoresView.defaults(config)
