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
Subdepartment Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.db import Session
from tailbone.views import MasterView


class SubdepartmentsView(MasterView):
    """
    Master view for the Subdepartment class.
    """
    model_class = model.Subdepartment
    has_versions = True

    grid_columns = [
        'number',
        'name',
        'department',
    ]

    mergeable = True
    merge_additive_fields = [
        'product_count',
    ]
    merge_fields = merge_additive_fields + [
        'uuid',
        'number',
        'name',
        'department_number',
    ]

    def configure_grid(self, g):
        super(SubdepartmentsView, self).configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('name')
        g.set_link('number')
        g.set_link('name')

    def configure_form(self, f):
        super(SubdepartmentsView, self).configure_form(f)
        f.remove_field('products')

        # TODO: figure out this dang department situation..
        f.remove_field('department_uuid')
        f.set_readonly('department')

    def get_merge_data(self, subdept):
        return {
            'uuid': subdept.uuid,
            'number': subdept.number,
            'name': subdept.name,
            'department_number': subdept.department.number if subdept.department else None,
            'product_count': len(subdept.products),
        }

    def merge_objects(self, removing, keeping):

        # merge products
        for product in removing.products:
            product.subdepartment = keeping

        Session.delete(removing)


def includeme(config):
    SubdepartmentsView.defaults(config)
