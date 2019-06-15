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
Employee Views
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa

from rattail.db import model

import colander
from deform import widget as dfwidget
from webhelpers2.html import tags, HTML

from tailbone import grids
from tailbone.db import Session
from tailbone.views import MasterView, AutocompleteView


class EmployeesView(MasterView):
    """
    Master view for the Employee class.
    """
    model_class = model.Employee
    has_versions = True

    labels = {
        'id': "ID",
    }

    grid_columns = [
        'id',
        'first_name',
        'last_name',
        'phone',
        'email',
        'status',
    ]

    form_fields = [
        'person',
        'first_name',
        'last_name',
        'display_name',
        'phone',
        'email',
        'status',
        'full_time',
        'full_time_start',
        'id',
        'stores',
        'departments',
    ]

    def configure_grid(self, g):
        super(EmployeesView, self).configure_grid(g)
        route_prefix = self.get_route_prefix()

        g.joiners['phone'] = lambda q: q.outerjoin(model.EmployeePhoneNumber, sa.and_(
            model.EmployeePhoneNumber.parent_uuid == model.Employee.uuid,
            model.EmployeePhoneNumber.preference == 1))
        g.joiners['email'] = lambda q: q.outerjoin(model.EmployeeEmailAddress, sa.and_(
            model.EmployeeEmailAddress.parent_uuid == model.Employee.uuid,
            model.EmployeeEmailAddress.preference == 1))

        g.filters['first_name'] = g.make_filter('first_name', model.Person.first_name)
        g.filters['last_name'] = g.make_filter('last_name', model.Person.last_name)

        g.filters['email'] = g.make_filter('email', model.EmployeeEmailAddress.address,
                                           label="Email Address")
        g.set_filter('phone', model.EmployeePhoneNumber.number,
                     label="Phone Number",
                     factory=grids.filters.AlchemyPhoneNumberFilter)

        # id
        if self.request.has_perm('{}.edit'.format(route_prefix)):
            g.set_link('id')
        else:
            g.hide_column('id')
            del g.filters['id']

        # status
        if self.request.has_perm('{}.edit'.format(route_prefix)):
            g.set_enum('status', self.enum.EMPLOYEE_STATUS)
            g.filters['status'].default_active = True
            g.filters['status'].default_verb = 'equal'
            # TODO: why must we set unicode string value here?
            g.filters['status'].default_value = six.text_type(self.enum.EMPLOYEE_STATUS_CURRENT)
        else:
            g.hide_column('status')
            del g.filters['status']

        g.filters['first_name'].default_active = True
        g.filters['first_name'].default_verb = 'contains'

        g.filters['last_name'].default_active = True
        g.filters['last_name'].default_verb = 'contains'

        g.sorters['first_name'] = lambda q, d: q.order_by(getattr(model.Person.first_name, d)())
        g.sorters['last_name'] = lambda q, d: q.order_by(getattr(model.Person.last_name, d)())

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.EmployeeEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.EmployeePhoneNumber.number, d)())

        g.set_sort_defaults('first_name')

        g.set_label('phone', "Phone Number")
        g.set_label('email', "Email Address")

        g.set_link('first_name')
        g.set_link('last_name')

    def query(self, session):
        q = session.query(model.Employee).join(model.Person)
        if not self.request.has_perm('employees.edit'):
            q = q.filter(model.Employee.status == self.enum.EMPLOYEE_STATUS_CURRENT)
        return q

    def editable_instance(self, employee):
        if self.rattail_config.demo():
            return not bool(employee.user and employee.user.username == 'chuck')
        return True

    def deletable_instance(self, employee):
        if self.rattail_config.demo():
            return not bool(employee.user and employee.user.username == 'chuck')
        return True

    def configure_form(self, f):
        super(EmployeesView, self).configure_form(f)
        employee = f.model_instance

        f.set_renderer('person', self.render_person)

        f.set_renderer('stores', self.render_stores)
        f.set_label('stores', "Stores") # TODO: should not be necessary
        if self.creating or self.editing:
            stores = self.get_possible_stores().all()
            store_values = [(s.uuid, six.text_type(s)) for s in stores]
            f.set_node('stores', colander.SchemaNode(colander.Set()))
            f.set_widget('stores', dfwidget.SelectWidget(multiple=True,
                                                         size=len(stores),
                                                         values=store_values))
            if self.editing:
                f.set_default('stores', [s.uuid for s in employee.stores])

        f.set_renderer('departments', self.render_departments)
        f.set_label('departments', "Departments") # TODO: should not be necessary
        if self.creating or self.editing:
            departments = self.get_possible_departments().all()
            dept_values = [(d.uuid, six.text_type(d)) for d in departments]
            f.set_node('departments', colander.SchemaNode(colander.Set()))
            f.set_widget('departments', dfwidget.SelectWidget(multiple=True,
                                                              size=len(departments),
                                                              values=dept_values))
            if self.editing:
                f.set_default('departments', [d.uuid for d in employee.departments])

        f.set_enum('status', self.enum.EMPLOYEE_STATUS)

        f.set_type('full_time_start', 'date_jquery')
        if self.editing:
            # TODO: this should not be needed (association proxy)
            f.set_default('full_time_start', employee.full_time_start)

        f.set_readonly('person')
        f.set_readonly('phone')
        f.set_readonly('email')

        f.set_label('display_name', "Short Name")
        f.set_label('phone', "Phone Number")
        f.set_label('email', "Email Address")

        if not self.viewing:
            f.remove_fields('first_name', 'last_name')

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated
        employee = super(EmployeesView, self).objectify(form, data)
        self.update_stores(employee, data)
        self.update_departments(employee, data)
        return employee

    def update_stores(self, employee, data):
        old_stores = set([s.uuid for s in employee.stores])
        new_stores = data['stores']
        for uuid in new_stores:
            if uuid not in old_stores:
                employee._stores.append(model.EmployeeStore(store_uuid=uuid))
        for uuid in old_stores:
            if uuid not in new_stores:
                store = self.Session.query(model.Store).get(uuid)
                employee.stores.remove(store)

    def update_departments(self, employee, data):
        old_depts = set([d.uuid for d in employee.departments])
        new_depts = data['departments']
        for uuid in new_depts:
            if uuid not in old_depts:
                employee._departments.append(model.EmployeeDepartment(department_uuid=uuid))
        for uuid in old_depts:
            if uuid not in new_depts:
                dept = self.Session.query(model.Department).get(uuid)
                employee.departments.remove(dept)

    def get_possible_stores(self):
        return self.Session.query(model.Store)\
                           .order_by(model.Store.name)

    def get_possible_departments(self):
        return self.Session.query(model.Department)\
                           .order_by(model.Department.name)

    def render_person(self, employee, field):
        person = employee.person if employee else None
        if not person:
            return ""
        text = six.text_type(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def render_stores(self, employee, field):
        stores = employee.stores if employee else None
        if not stores:
            return ""
        items = []
        for store in sorted(stores, key=six.text_type):
            items.append(HTML.tag('li', c=six.text_type(store)))
        return HTML.tag('ul', c=items)

    def render_departments(self, employee, field):
        departments = employee.departments if employee else None
        if not departments:
            return ""
        items = []
        for department in sorted(departments, key=six.text_type):
            items.append(HTML.tag('li', c=six.text_type(department)))
        return HTML.tag('ul', c=items)

    def get_version_child_classes(self):
        return [
            (model.Person, 'uuid', 'person_uuid'),
            (model.EmployeePhoneNumber, 'parent_uuid'),
            (model.EmployeeEmailAddress, 'parent_uuid'),
            (model.EmployeeStore, 'employee_uuid'),
            (model.EmployeeDepartment, 'employee_uuid'),
        ]


class EmployeesAutocomplete(AutocompleteView):
    """
    Autocomplete view for the Employee model, but restricted to return only
    results for current employees.
    """
    mapped_class = model.Person
    fieldname = 'display_name'

    def filter_query(self, q):
        return q.join(model.Employee)\
            .filter(model.Employee.status == self.enum.EMPLOYEE_STATUS_CURRENT)

    def value(self, person):
        return person.employee.uuid


def includeme(config):

    # autocomplete
    config.add_route('employees.autocomplete',  '/employees/autocomplete')
    config.add_view(EmployeesAutocomplete, route_name='employees.autocomplete',
                    renderer='json', permission='employees.list')

    EmployeesView.defaults(config)
