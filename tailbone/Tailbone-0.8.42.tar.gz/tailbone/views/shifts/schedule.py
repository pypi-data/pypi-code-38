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
Views for employee schedules
"""

from __future__ import unicode_literals, absolute_import

import datetime

from rattail.db import model
from rattail.time import localtime, make_utc, get_sunday

from tailbone.db import Session
from tailbone.views.shifts.lib import TimeSheetView


class ScheduleView(TimeSheetView):
    """
    Simple view for current user's schedule.
    """
    key = 'schedule'
    model_class = model.ScheduledShift

    def edit(self):
        """
        View for editing (full) schedule.
        """
        # first check if we should clear the schedule
        if self.request.method == 'POST' and self.request.POST.get('clear-schedule') == 'clear':
            count = self.clear_schedule()
            self.request.session.flash("Removed {} shifts from current schedule.".format(count))
            return self.redirect(self.request.route_url('schedule.edit'))

        # okay then, check if we should copy data from another week
        if self.request.method == 'POST' and self.request.POST.get('copy-week'):
            sunday, copied = self.copy_schedule()
            self.request.session.flash("Copied {} shifts from week of {}".format(copied, sunday.strftime('%m/%d/%Y')))
            return self.redirect(self.request.route_url('schedule.edit'))

        # okay then, process filters; redirect if any were received
        context = self.get_timesheet_context()
        form = self.make_full_filter_form(context)
        self.process_filter_form(form)

        # okay then, maybe process saved shift data
        if self.request.method == 'POST':

            # organize form data by uuid / field
            fields = ['employee_uuid', 'store_uuid', 'start_time', 'end_time', 'delete']
            data = dict([(f, {}) for f in fields])
            for key in self.request.POST:
                for field in fields:
                    if key.startswith('{}-'.format(field)):
                        uuid = key[len('{}-'.format(field)):]
                        if uuid:
                            data[field][uuid] = self.request.POST[key]
                        break

            # apply delete operations
            deleted = []
            for uuid, value in data['delete'].items():
                if value == 'delete':
                    shift = Session.query(model.ScheduledShift).get(uuid)
                    if shift:
                        Session.delete(shift)
                        deleted.append(uuid)

            # apply create / update operations
            created = {}
            updated = {}
            time_format = '%a %d %b %Y %I:%M %p'
            for uuid, employee_uuid in data['start_time'].items():
                if uuid in deleted:
                    continue
                if uuid.startswith('new-'):
                    shift = model.ScheduledShift()
                    shift.employee_uuid = data['employee_uuid'][uuid]
                    if 'store_uuid' in data and uuid in data['store_uuid']:
                        shift.store_uuid = data['store_uuid'][uuid]
                    else:
                        shift.store_uuid = context['store'].uuid if context['store'] else None
                    Session.add(shift)
                    created[uuid] = shift
                else:
                    shift = Session.query(model.ScheduledShift).get(uuid)
                    assert shift
                    updated[uuid] = shift
                start_time = datetime.datetime.strptime(data['start_time'][uuid], time_format)
                shift.start_time = make_utc(localtime(self.rattail_config, start_time))
                end_time = datetime.datetime.strptime(data['end_time'][uuid], time_format)
                shift.end_time = make_utc(localtime(self.rattail_config, end_time))

            self.request.session.flash("Changes were applied: created {}, updated {}, "
                                       "deleted {} Scheduled Shifts".format(
                                           len(created), len(updated), len(deleted)))
            return self.redirect(self.request.route_url('schedule.edit'))

        context['form'] = form
        context['page_title'] = "Edit Schedule"
        context['allow_clear'] = self.rattail_config.getbool('tailbone', 'schedule.allow_clear',
                                                             default=True)
        return self.render_full(**context)

    def clear_schedule(self):
        deleted = 0
        context = self.get_timesheet_context()
        if context['employees']:
            sunday = datetime.datetime.combine(context['date'], datetime.time(0))
            start_time = localtime(self.rattail_config, sunday)
            end_time = localtime(self.rattail_config, sunday + datetime.timedelta(days=7))
            shifts = Session.query(model.ScheduledShift)\
                            .filter(model.ScheduledShift.employee_uuid.in_([e.uuid for e in context['employees']]))\
                            .filter(model.ScheduledShift.start_time >= make_utc(start_time))\
                            .filter(model.ScheduledShift.end_time < make_utc(end_time))
            for shift in shifts:
                Session.delete(shift)
                deleted += 1
        return deleted

    def copy_schedule(self):
        """
        Clear current schedule, then copy shift data from another week.
        """
        try:
            sunday = datetime.datetime.strptime(self.request.POST['copy-week'], '%m/%d/%Y').date()
        except ValueError as error:
            self.request.session.flash("Invalid date specified: {}: {}".format(type(error), error), 'error')
            raise self.redirect(self.request.route_url('schedule.edit'))
        sunday = get_sunday(sunday)
        context = self.get_timesheet_context()
        if sunday == context['date']:
            self.request.session.flash("Cannot copy schedule from same week; please specify a different week.", 'error')
            raise self.redirect(self.request.route_url('schedule.edit'))

        self.clear_schedule()

        copied = 0
        if context['employees']:
            offset = context['date'] - sunday
            sunday = datetime.datetime.combine(sunday, datetime.time(0))
            start_time = localtime(self.rattail_config, sunday)
            end_time = localtime(self.rattail_config, sunday + datetime.timedelta(days=7))
            shifts = Session.query(model.ScheduledShift)\
                            .filter(model.ScheduledShift.employee_uuid.in_([e.uuid for e in context['employees']]))\
                            .filter(model.ScheduledShift.start_time >= make_utc(start_time))\
                            .filter(model.ScheduledShift.end_time < make_utc(end_time))
            for shift in shifts:

                # must calculate new times using date as base, b/c of daylight savings
                start_time = localtime(self.rattail_config, shift.start_time, from_utc=True)
                start_time = datetime.datetime.combine(start_time.date() + offset, start_time.time())
                start_time = localtime(self.rattail_config, start_time)
                end_time = localtime(self.rattail_config, shift.end_time, from_utc=True)
                end_time = datetime.datetime.combine(end_time.date() + offset, end_time.time())
                end_time = localtime(self.rattail_config, end_time)

                Session.add(model.ScheduledShift(
                    employee_uuid=shift.employee_uuid,
                    store_uuid=shift.store_uuid,
                    start_time=make_utc(start_time),
                    end_time=make_utc(end_time),
                ))
                copied += 1

        return sunday, copied

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)

        # edit schedule
        config.add_route('schedule.edit', '/schedule/edit')
        config.add_view(cls, attr='edit', route_name='schedule.edit',
                        renderer='/shifts/schedule_edit.mako',
                        permission='schedule.edit')
        config.add_tailbone_permission('schedule', 'schedule.edit', "Edit full schedule")

        # printing "any" schedule requires this permission
        config.add_tailbone_permission('schedule', 'schedule.print', "Print schedule")

        # print full schedule
        config.add_route('schedule.print', '/schedule/print')
        config.add_view(cls, attr='full', route_name='schedule.print',
                        renderer='/shifts/schedule_print.mako',
                        permission='schedule.print')

        # print employee schedule
        config.add_route('schedule.employee.print', '/schedule/employee/print')
        config.add_view(cls, attr='employee', route_name='schedule.employee.print',
                        renderer='/shifts/schedule_print_employee.mako',
                        permission='schedule.print')


def includeme(config):
    ScheduleView.defaults(config)
