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
Views for employee time sheets
"""

from __future__ import unicode_literals, absolute_import

import datetime

from rattail.db import model
from rattail.time import make_utc, localtime

from tailbone.db import Session
from tailbone.views.shifts.lib import TimeSheetView as BaseTimeSheetView


class TimeSheetView(BaseTimeSheetView):
    """
    Views for employee time sheets, i.e. worked shift data
    """
    key = 'timesheet'
    title = "Time Sheet"
    model_class = model.WorkedShift

    def edit_employee(self):
        """
        View for editing single employee's timesheet
        """
        # process filters; redirect if any were received
        context = self.get_employee_context()
        form = self.make_employee_filter_form(context)
        self.process_employee_filter_form(form)

        # okay then, maybe process saved shift data
        if self.request.method == 'POST':

            # TODO: most of this is copied from 'schedule.edit' view, should merge...

            # organize form data by uuid / field
            fields = ['start_time', 'end_time', 'delete']
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
            for uuid, value in list(data['delete'].items()):
                assert value == 'delete'
                shift = Session.query(model.WorkedShift).get(uuid)
                assert shift
                Session.delete(shift)
                deleted.append(uuid)

            # apply create / update operations
            created = {}
            updated = {}
            time_format = '%a %d %b %Y %I:%M %p'
            for uuid, time in data['start_time'].items():
                if uuid in deleted:
                    continue
                if uuid.startswith('new-'):
                    shift = model.WorkedShift()
                    shift.employee_uuid = context['employee'].uuid
                    # TODO: add support for setting store here...
                    Session.add(shift)
                    created[uuid] = shift
                else:
                    shift = Session.query(model.WorkedShift).get(uuid)
                    assert shift
                    updated[uuid] = shift

                start_time = data['start_time'][uuid] or None
                if start_time:
                    start_time = datetime.datetime.strptime(start_time, time_format)
                    shift.start_time = make_utc(localtime(self.rattail_config, start_time))
                else:
                    shift.start_time = None

                end_time = data['end_time'][uuid] or None
                if end_time:
                    end_time = datetime.datetime.strptime(end_time, time_format)
                    shift.end_time = make_utc(localtime(self.rattail_config, end_time))
                else:
                    shift.end_time = None

            self.request.session.flash("Changes were applied: created {}, updated {}, "
                                       "deleted {} Worked Shifts".format(
                                           len(created), len(updated), len(deleted)))
            return self.redirect(self.request.route_url('timesheet.employee.edit'))

        context['form'] = form
        context['page_title'] = "Edit Employee Time Sheet"
        return self.render_single(**context)

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)

        # edit employee time sheet
        config.add_tailbone_permission('timesheet', 'timesheet.edit',
                                       "Edit time sheet (for *any* employee!)")
        config.add_route('timesheet.employee.edit', '/timesheeet/employee/edit')
        config.add_view(cls, attr='edit_employee', route_name='timesheet.employee.edit',
                        renderer='/shifts/timesheet_edit.mako',
                        permission='timesheet.edit')


def includeme(config):
    TimeSheetView.defaults(config)
