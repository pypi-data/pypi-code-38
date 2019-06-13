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
Common stuff for tempmon views
"""

from __future__ import unicode_literals, absolute_import

from rattail_tempmon.db import Session as RawTempmonSession

from webhelpers2.html import HTML

from tailbone import views, grids
from tailbone.db import TempmonSession


class MasterView(views.MasterView):
    """
    Base class for tempmon views.
    """
    Session = TempmonSession

    def get_bulk_delete_session(self):
        return RawTempmonSession()

    def render_probes(self, obj, field):
        """
        This method is used by Appliance and Client views.
        """
        if not obj.probes:
            return ""

        route_prefix = self.get_route_prefix()
        view_url = lambda p, i: self.request.route_url('tempmon.probes.view', uuid=p.uuid)
        actions = [
            grids.GridAction('view', icon='zoomin', url=view_url),
        ]
        if self.request.has_perm('tempmon.probes.edit'):
            url = lambda p, i: self.request.route_url('tempmon.probes.edit', uuid=p.uuid)
            actions.append(grids.GridAction('edit', icon='pencil', url=url))

        g = grids.Grid(
            key='{}.probes'.format(route_prefix),
            data=obj.probes,
            columns=[
                'description',
                'critical_temp_min',
                'good_temp_min',
                'good_temp_max',
                'critical_temp_max',
                'status',
                'enabled',
            ],
            labels={
                'critical_temp_min': "Crit. Min",
                'good_temp_min': "Good Min",
                'good_temp_max': "Good Max",
                'critical_temp_max': "Crit. Max",
            },
            url=lambda p: self.request.route_url('tempmon.probes.view', uuid=p.uuid),
            linked_columns=['description'],
            main_actions=actions,
        )
        g.set_enum('status', self.enum.TEMPMON_PROBE_STATUS)
        g.set_type('enabled', 'boolean')
        return HTML.literal(g.render_grid())
