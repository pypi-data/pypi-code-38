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
DataSync Views
"""

from __future__ import unicode_literals, absolute_import

import subprocess
import logging

from rattail.db import model

from tailbone.views import MasterView


log = logging.getLogger(__name__)


class DataSyncChangesView(MasterView):
    """
    Master view for the DataSyncChange model.
    """
    model_class = model.DataSyncChange
    url_prefix = '/datasync/changes'
    permission_prefix = 'datasync'
    creatable = False
    editable = False
    bulk_deletable = True

    grid_columns = [
        'source',
        'payload_type',
        'payload_key',
        'deletion',
        'obtained',
        'consumer',
    ]

    def configure_grid(self, g):
        super(DataSyncChangesView, self).configure_grid(g)
        g.set_sort_defaults('obtained')
        g.set_type('obtained', 'datetime')

    def template_kwargs_index(self, **kwargs):
        kwargs['allow_filemon_restart'] = bool(self.rattail_config.get('tailbone', 'filemon.restart'))
        return kwargs

    def restart(self):
        # TODO: Add better validation (e.g. CSRF) here?
        if self.request.method == 'POST':
            cmd = self.rattail_config.getlist('tailbone', 'datasync.restart', default='/bin/sleep 3') # simulate by default
            log.debug("attempting datasync restart with command: {}".format(cmd))
            result = subprocess.call(cmd)
            if result == 0:
                self.request.session.flash("DataSync daemon has been restarted.")
            else:
                self.request.session.flash("DataSync daemon could not be restarted; result was: {}".format(result), 'error')
        return self.redirect(self.request.get_referrer(default=self.request.route_url('datasyncchanges')))

    def mobile_index(self):
        return {}

    @classmethod
    def defaults(cls, config):

        # fix permission group title
        config.add_tailbone_permission_group('datasync', label="DataSync")

        # restart datasync
        config.add_tailbone_permission('datasync', 'datasync.restart', label="Restart DataSync Daemon")
        # desktop
        config.add_route('datasync.restart', '/datasync/restart')
        config.add_view(cls, attr='restart', route_name='datasync.restart', permission='datasync.restart')
        # mobile
        config.add_route('datasync.mobile', '/mobile/datasync/')
        config.add_view(cls, attr='mobile_index', route_name='datasync.mobile',
                        permission='datasync.restart', renderer='/mobile/datasync.mako')

        cls._defaults(config)


def includeme(config):
    DataSyncChangesView.defaults(config)
