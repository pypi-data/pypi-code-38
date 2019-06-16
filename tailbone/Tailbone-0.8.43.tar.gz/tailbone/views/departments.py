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
Department Views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from deform import widget as dfwidget

from tailbone import grids
from tailbone.views import MasterView, AutocompleteView


class DepartmentsView(MasterView):
    """
    Master view for the Department class.
    """
    model_class = model.Department
    has_versions = True

    grid_columns = [
        'number',
        'name',
        'product',
        'personnel',
        'exempt_from_gross_sales',
    ]

    def configure_grid(self, g):
        super(DepartmentsView, self).configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('number')
        g.set_type('product', 'boolean')
        g.set_type('personnel', 'boolean')
        g.set_link('number')
        g.set_link('name')

    def configure_form(self, f):
        super(DepartmentsView, self).configure_form(f)
        f.remove_field('subdepartments')
        f.remove_field('employees')
        f.set_type('product', 'boolean')
        f.set_type('personnel', 'boolean')

    def template_kwargs_view(self, **kwargs):
        department = kwargs['instance']
        if department.employees:
            employees = sorted(department.employees, key=six.text_type)
            actions = [
                grids.GridAction('view', icon='zoomin',
                                 url=lambda r, i: self.request.route_url('employees.view', uuid=r.uuid))
            ]
            kwargs['employees'] = grids.Grid(None, employees, ['display_name'], request=self.request,
                                             model_class=model.Employee, main_actions=actions)
        else:
            kwargs['employees'] = None
        return kwargs

    def list_by_vendor(self):
        """
        View list of departments by vendor
        """
        data = self.Session.query(model.Department)\
                           .outerjoin(model.Product)\
                           .join(model.ProductCost)\
                           .join(model.Vendor)\
                           .filter(model.Vendor.uuid == self.request.params['uuid'])\
                           .distinct()\
                           .order_by(model.Department.name)

        def configure(g):
            g.configure(include=[
                g.name,
            ], readonly=True)

        def row_attrs(row, i):
            return {'data-uuid': row.uuid}

        grid = self.make_grid(data=data, sortable=False, filterable=False, pageable=False,
                              configure=configure, width=None, checkboxes=True,
                              row_attrs=row_attrs, main_actions=[], more_actions=[])
        self.request.response.content_type = str('text/html')
        self.request.response.text = grid.render_grid()
        return self.request.response

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # list by vendor
        config.add_route('{}.by_vendor'.format(route_prefix), '{}/by-vendor'.format(url_prefix))
        config.add_view(cls, attr='list_by_vendor', route_name='{}.by_vendor'.format(route_prefix),
                        permission='{}.list'.format(permission_prefix))

        cls._defaults(config)


class DepartmentsAutocomplete(AutocompleteView):

    mapped_class = model.Department
    fieldname = 'name'


def includeme(config):

    # autocomplete
    config.add_route('departments.autocomplete',        '/departments/autocomplete')
    config.add_view(DepartmentsAutocomplete, route_name='departments.autocomplete',
                    renderer='json', permission='departments.list')

    DepartmentsView.defaults(config)
