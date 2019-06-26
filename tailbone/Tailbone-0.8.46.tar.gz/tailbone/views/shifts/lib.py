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
Base views for time sheets
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa

from rattail import enum
from rattail.db import model, api
from rattail.time import localtime, make_utc, get_sunday
from rattail.util import pretty_hours, hours_as_decimal

import colander
from deform import widget as dfwidget
from webhelpers2.html import tags, HTML

from tailbone import forms
from tailbone.db import Session
from tailbone.views import View


class ShiftFilter(colander.Schema):

    store = colander.SchemaNode(forms.types.StoreType())

    department = colander.SchemaNode(forms.types.DepartmentType())

    date = colander.SchemaNode(colander.Date())


class EmployeeShiftFilter(colander.Schema):

    employee = colander.SchemaNode(forms.types.EmployeeType())

    date = colander.SchemaNode(colander.Date())


class TimeSheetView(View):
    """
    Base view for time sheets.
    """
    key = None
    title = None
    model_class = None
    expose_employee_views = True

    # Set this to False to avoid the default behavior of auto-filtering by
    # current store.
    default_filter_store = True

    @classmethod
    def get_title(cls):
        return cls.title or cls.key.capitalize()

    @classmethod
    def get_url_prefix(cls):
        return getattr(cls, 'url_prefix', cls.key).rstrip('/')

    def get_timesheet_context(self):
        """
        Determine date/store/dept context from user's session and/or defaults.
        """
        date = None
        date_key = 'timesheet.{}.date'.format(self.key)
        if date_key in self.request.session:
            date_value = self.request.session.get(date_key)
            if date_value:
                try:
                    date = datetime.datetime.strptime(date_value, '%m/%d/%Y').date()
                except ValueError:
                    pass
        if not date:
            date = localtime(self.rattail_config).date()

        store = None
        department = None
        store_key = 'timesheet.{}.store'.format(self.key)
        department_key = 'timesheet.{}.department'.format(self.key)
        if store_key in self.request.session or department_key in self.request.session:
            store_uuid = self.request.session.get(store_key)
            if store_uuid:
                store = Session.query(model.Store).get(store_uuid) if store_uuid else None
            department_uuid = self.request.session.get(department_key)
            if department_uuid:
                department = Session.query(model.Department).get(department_uuid)
        else: # no store/department in session
            if self.default_filter_store:
                store = self.rattail_config.get('rattail', 'store')
                if store:
                    store = api.get_store(Session(), store)

        employees = Session.query(model.Employee)\
                           .filter(model.Employee.status == enum.EMPLOYEE_STATUS_CURRENT)
        if store:
            employees = employees.join(model.EmployeeStore)\
                                 .filter(model.EmployeeStore.store == store)
        if department:
            employees = employees.join(model.EmployeeDepartment)\
                                 .filter(model.EmployeeDepartment.department == department)

        return {
            'date': date,
            'store': store,
            'department': department,
            'employees': employees.all(),
        }

    def get_employee_context(self):
        """
        Determine employee/date context from user's session and/or defaults
        """
        date = None
        date_key = 'timesheet.{}.employee.date'.format(self.key)
        if date_key in self.request.session:
            date_value = self.request.session.get(date_key)
            if date_value:
                try:
                    date = datetime.datetime.strptime(date_value, '%m/%d/%Y').date()
                except ValueError:
                    pass
        if not date:
            date = localtime(self.rattail_config).date()

        employee = None
        employee_key = 'timesheet.{}.employee'.format(self.key)
        if employee_key in self.request.session:
            employee_uuid = self.request.session[employee_key]
            employee = Session.query(model.Employee).get(employee_uuid) if employee_uuid else None
        if not employee:
            employee = self.request.user.employee

        # force current user if not allowed to view all data
        if not self.request.has_perm('{}.viewall'.format(self.key)):
            employee = self.request.user.employee
            assert employee

        return {'date': date, 'employee': employee}

    def process_filter_form(self, form):
        """
        Process a "shift filter" form if one was in fact POST'ed.  If it was
        then we store new context in session and redirect to display as normal.
        """
        if form.validate(newstyle=True):
            store = form.validated['store']
            self.request.session['timesheet.{}.store'.format(self.key)] = store.uuid if store else None
            department = form.validated['department']
            self.request.session['timesheet.{}.department'.format(self.key)] = department.uuid if department else None
            date = form.validated['date']
            self.request.session['timesheet.{}.date'.format(self.key)] = date.strftime('%m/%d/%Y') if date else None
            raise self.redirect(self.request.current_route_url())

    def process_employee_filter_form(self, form):
        """
        Process an "employee shift filter" form if one was in fact POST'ed.  If it
        was then we store new context in session and redirect to display as normal.
        """
        if form.validate(newstyle=True):
            employee = form.validated['employee']
            self.request.session['timesheet.{}.employee'.format(self.key)] = employee.uuid if employee else None
            date = form.validated['date']
            self.request.session['timesheet.{}.employee.date'.format(self.key)] = date.strftime('%m/%d/%Y') if date else None
            raise self.redirect(self.request.current_route_url())

    def make_full_filter_form(self, context):
        form = forms.Form(schema=ShiftFilter(), request=self.request)

        stores = self.get_stores()
        store_values = [(s.uuid, "{} - {}".format(s.id, s.name)) for s in stores]
        store_values.insert(0, ('', "(all)"))
        form.set_widget('store', forms.widgets.PlainSelectWidget(values=store_values))
        if context['store']:
            form.set_default('store', context['store'].uuid)
        else:
            # TODO: why is this necessary? somehow the previous store is being
            # preserved as the "default" when switching from single store view
            # to "all stores" view
            form.set_default('store', '')

        departments = self.get_departments()
        department_values = [(d.uuid, d.name) for d in departments]
        department_values.insert(0, ('', "(all)"))
        form.set_widget('department', forms.widgets.PlainSelectWidget(values=department_values))
        if context['department']:
            form.set_default('department', context['department'].uuid)
        else:
            # TODO: why is this necessary? somehow the previous dept is being
            # preserved as the "default" when switching from single dept view
            # to "all depts" view
            form.set_default('department', '')

        form.set_type('date', 'date_jquery')
        form.set_default('date', get_sunday(context['date']))
        return form

    def full(self):
        """
        View a "full" timesheet/schedule, i.e. all employees but filterable by
        store and/or department.
        """
        context = self.get_timesheet_context()
        form = self.make_full_filter_form(context)
        self.process_filter_form(form)
        context['form'] = form
        return self.render_full(**context)

    def make_employee_filter_form(self, context):
        """
        View time sheet for single employee.
        """
        permission_prefix = self.key
        form = forms.Form(schema=EmployeeShiftFilter(), request=self.request)

        if self.request.has_perm('{}.viewall'.format(permission_prefix)):
            employee_display = six.text_type(context['employee'] or '')
            employees_url = self.request.route_url('employees.autocomplete')
            form.set_widget('employee', forms.widgets.JQueryAutocompleteWidget(
                field_display=employee_display, service_url=employees_url))
            if context['employee']:
                form.set_default('employee', context['employee'].uuid)
        else:
            form.set_widget('employee', forms.widgets.ReadonlyWidget())
            form.set_default('employee', context['employee'].uuid)

        form.set_type('date', 'date_jquery')
        form.set_default('date', get_sunday(context['date']))
        return form

    def employee(self):
        """
        View time sheet for single employee.
        """
        context = self.get_employee_context()
        form = self.make_employee_filter_form(context)
        self.process_employee_filter_form(form)
        context['form'] = form
        return self.render_single(**context)

    def crossview(self):
        """
        Update session storage to so 'other' view reflects current view
        filters, then redirect to other view.
        """
        other_key = 'timesheet' if self.key == 'schedule' else 'schedule'

        # TODO: this check is pretty hacky..
        # employee time sheet
        if 'employee' in self.request.get_referrer():
            self.session_put('employee', self.session_get('employee'), mainkey=other_key)
            self.session_put('employee.date', self.session_get('employee.date'), mainkey=other_key)
            return self.redirect(self.request.route_url('{}.employee'.format(other_key)))

        else: # full time sheet
            self.session_put('store', self.session_get('store'), mainkey=other_key)
            self.session_put('department', self.session_get('department'), mainkey=other_key)
            self.session_put('date', self.session_get('date'), mainkey=other_key)
            return self.redirect(self.request.route_url(other_key))

    def session_get(self, key, mainkey=None):
        if mainkey is None:
            mainkey = self.key
        return self.request.session.get('timesheet.{}.{}'.format(mainkey, key))

    def session_put(self, key, value, mainkey=None):
        if mainkey is None:
            mainkey = self.key
        self.request.session['timesheet.{}.{}'.format(mainkey, key)] = value

    def get_stores(self):
        return Session.query(model.Store).order_by(model.Store.id).all()

    def get_store_options(self, stores):
        options = [tags.Option("{} - {}".format(s.id, s.name), s.uuid) for s in stores]
        return tags.Options(options, prompt="(all)")

    def get_departments(self):
        return Session.query(model.Department).order_by(model.Department.name).all()

    def get_department_options(self, departments):
        options = [tags.Option(d.name, d.uuid) for d in departments]
        return tags.Options(options, prompt="(all)")

    def render_full(self, date=None, employees=None, store=None, department=None, form=None, **kwargs):
        """
        Render a time sheet for one or more employees, for the week which
        includes the specified date.
        """
        sunday = get_sunday(date)
        weekdays = [sunday]
        for i in range(1, 7):
            weekdays.append(sunday + datetime.timedelta(days=i))

        saturday = weekdays[-1]
        if saturday.year == sunday.year:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d'), saturday.strftime('%a %b %d, %Y'))
        else:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d, %Y'), saturday.strftime('%a %b %d, %Y'))

        self.modify_employees(employees, weekdays)

        stores = self.get_stores()
        store_options = self.get_store_options(stores)

        departments = self.get_departments()
        department_options = self.get_department_options(departments)

        context = {
            'page_title': self.get_title_full(),
            'form': form,
            'dform': form.make_deform_form() if form else None,
            'employees': employees,
            'stores': stores,
            'store_options': store_options,
            'store': store,
            'departments': departments,
            'department_options': department_options,
            'department': department,
            'week_of': week_of,
            'sunday': sunday,
            'prev_sunday': sunday - datetime.timedelta(days=7),
            'next_sunday': sunday + datetime.timedelta(days=7),
            'weekdays': weekdays,
            'permission_prefix': self.key,
            'render_shift': self.render_shift,
        }
        context.update(kwargs)
        return context

    def get_title_full(self):
        return "Full {}".format(self.get_title())

    def render_shift(self, shift):
        return HTML.tag('span', c=shift.get_display(self.rattail_config))

    def render_single(self, date=None, employee=None, form=None, **kwargs):
        """
        Render a time sheet for one employee, for the week which includes the
        specified date.
        """
        sunday = get_sunday(date)
        weekdays = [sunday]
        for i in range(1, 7):
            weekdays.append(sunday + datetime.timedelta(days=i))

        saturday = weekdays[-1]
        if saturday.year == sunday.year:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d'), saturday.strftime('%a %b %d, %Y'))
        else:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d, %Y'), saturday.strftime('%a %b %d, %Y'))

        self.modify_employees([employee], weekdays)

        context = {
            'single': True,
            'page_title': "Employee {}".format(self.get_title()),
            'form': form,
            'dform': form.make_deform_form() if form else None,
            'employee': employee,
            'employees': [employee],
            'week_of': week_of,
            'sunday': sunday,
            'prev_sunday': sunday - datetime.timedelta(days=7),
            'next_sunday': sunday + datetime.timedelta(days=7),
            'weekdays': weekdays,
            'permission_prefix': self.key,
            'render_shift': self.render_shift,
        }
        context.update(kwargs)
        return context

    def modify_employees(self, employees, weekdays):
        self.fetch_shift_data(self.model_class, employees, weekdays)

    def fetch_shift_data(self, cls, employees, weekdays):
        """
        Fetch all shift data of the given model class (``cls``), according to
        the given params.  The cached shift data is attached to each employee.
        """
        # TODO: a bit hacky, this?  display hours as HH:MM by default, but
        # check config in order to display as HH.HH for certain users
        hours_style = 'pretty'
        if self.request.user:
            hours_style = self.rattail_config.get('tailbone', 'hours_style.{}'.format(self.request.user.username),
                                                  default='pretty')
        if hours_style != 'decimal':
            hours_style = 'pretty'

        shift_type = 'scheduled' if cls is model.ScheduledShift else 'worked'
        min_time = localtime(self.rattail_config, datetime.datetime.combine(weekdays[0], datetime.time(0)))
        max_time = localtime(self.rattail_config, datetime.datetime.combine(weekdays[-1] + datetime.timedelta(days=1), datetime.time(0)))
        shifts = Session.query(cls)\
                        .filter(cls.employee_uuid.in_([e.uuid for e in employees]))\
                        .filter(sa.or_(
                            sa.and_(
                                cls.start_time >= make_utc(min_time),
                                cls.start_time < make_utc(max_time),
                            ),
                            sa.and_(
                                cls.start_time == None,
                                cls.end_time >= make_utc(min_time),
                                cls.end_time < make_utc(max_time),
                            )))\
                        .all()

        for employee in employees:
            employee_shifts = sorted([s for s in shifts if s.employee_uuid == employee.uuid],
                                     key=lambda s: s.start_time or s.end_time)
            if not hasattr(employee, 'weekdays'):
                employee.weekdays = [{} for day in weekdays]
            setattr(employee, '{}_hours'.format(shift_type), datetime.timedelta(0))
            setattr(employee, '{}_hours_display'.format(shift_type), '0')
            hours_incomplete = False

            for i, day in enumerate(weekdays):
                empday = {
                    '{}_shifts'.format(shift_type): [],
                    '{}_hours'.format(shift_type): datetime.timedelta(0),
                    '{}_hours_display'.format(shift_type): '',
                    'hours_incomplete': False,
                }

                while employee_shifts:
                    shift = employee_shifts[0]
                    if shift.employee_uuid != employee.uuid:
                        break
                    elif shift.get_date(self.rattail_config) == day:
                        empday['{}_shifts'.format(shift_type)].append(shift)
                        length = shift.length
                        if length is not None:
                            empday['{}_hours'.format(shift_type)] += shift.length
                            setattr(employee, '{}_hours'.format(shift_type),
                                    getattr(employee, '{}_hours'.format(shift_type)) + shift.length)
                        else:
                            hours_incomplete = True
                            empday['hours_incomplete'] = True
                        del employee_shifts[0]
                    else:
                        break

                hours = empday['{}_hours'.format(shift_type)]
                if hours:
                    if hours_style == 'pretty':
                        display = pretty_hours(hours)
                    else: # decimal
                        display = six.text_type(hours_as_decimal(hours))
                    if empday['hours_incomplete']:
                        display = '{} ?'.format(display)
                    empday['{}_hours_display'.format(shift_type)] = display
                employee.weekdays[i].update(empday)

            hours = getattr(employee, '{}_hours'.format(shift_type))
            if hours:
                if hours_style == 'pretty':
                    display = pretty_hours(hours)
                else: # decimal
                    display = six.text_type(hours_as_decimal(hours))
                if hours_incomplete:
                    display = '{} ?'.format(display)
                setattr(employee, '{}_hours_display'.format(shift_type), display)

    @classmethod
    def defaults(cls, config):
        """
        Provide default configuration for a time sheet view.
        """
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):
        """
        Provide default configuration for a time sheet view.
        """
        title = cls.get_title()
        url_prefix = cls.get_url_prefix()
        config.add_tailbone_permission_group(cls.key, title)
        config.add_tailbone_permission(cls.key, '{}.viewall'.format(cls.key), "View full {}".format(title))

        # full time sheet
        config.add_route(cls.key, '{}/'.format(url_prefix))
        config.add_view(cls, attr='full', route_name=cls.key,
                        renderer='/shifts/{}.mako'.format(cls.key),
                        permission='{}.viewall'.format(cls.key))

        # single employee time sheet
        if cls.expose_employee_views:
            config.add_tailbone_permission(cls.key, '{}.view'.format(cls.key), "View single employee {}".format(title))
            config.add_route('{}.employee'.format(cls.key), '{}/employee/'.format(url_prefix))
            config.add_view(cls, attr='employee', route_name='{}.employee'.format(cls.key),
                            renderer='/shifts/{}.mako'.format(cls.key),
                            permission='{}.view'.format(cls.key))

        # goto cross-view (view 'timesheet' as 'schedule' or vice-versa)
        other_key = 'timesheet' if cls.key == 'schedule' else 'schedule'
        config.add_route('{}.goto.{}'.format(cls.key, other_key), '{}/goto-{}'.format(url_prefix, other_key))
        config.add_view(cls, attr='crossview', route_name='{}.goto.{}'.format(cls.key, other_key),
                        permission='{}.view'.format(other_key))
