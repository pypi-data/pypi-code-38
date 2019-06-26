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
Category Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone import forms
from tailbone.views import MasterView


class CategoriesView(MasterView):
    """
    Master view for the Category class.
    """
    model_class = model.Category
    model_title_plural = "Categories"
    route_prefix = 'categories'
    has_versions = True
    results_downloadable_xlsx = True

    grid_columns = [
        'code',
        'name',
        'department',
    ]

    form_fields = [
        'code',
        'name',
        'department',
    ]

    def configure_grid(self, g):
        super(CategoriesView, self).configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'

        g.set_joiner('department', lambda q: q.outerjoin(model.Department))
        g.set_sorter('department', model.Department.name)
        g.set_filter('department', model.Department.name)

        g.set_sort_defaults('code')
        g.set_link('code')
        g.set_link('name')

    def get_xlsx_fields(self):
        fields = super(CategoriesView, self).get_xlsx_fields()
        fields.extend([
            'department_number',
            'department_name',
        ])
        return fields

    def get_xlsx_row(self, category, fields):
        row = super(CategoriesView, self).get_xlsx_row(category, fields)
        dept = category.department
        if dept:
            row['department_number'] = dept.number
            row['department_name'] = dept.name
        else:
            row['department_number'] = None
            row['department_name'] = None
        return row

    def configure_form(self, f):
        super(CategoriesView, self).configure_form(f)

        # department
        if self.creating or self.editing:
            if 'department' in f:
                f.replace('department', 'department_uuid')
                f.set_label('department_uuid', "Department")
                dept_values = self.get_department_values()
                dept_values.insert(0, ('', "(none)"))
                f.set_widget('department_uuid', forms.widgets.JQuerySelectWidget(values=dept_values))
        else:
            f.set_readonly('department')

    def get_department_values(self):
        departments = self.Session.query(model.Department)\
                                  .order_by(model.Department.number)
        return [(dept.uuid, "{} {}".format(dept.number, dept.name))
                for dept in departments]


def includeme(config):
    CategoriesView.defaults(config)
