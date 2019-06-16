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
FileMon Views
"""

from __future__ import unicode_literals, absolute_import

import subprocess
import logging

from tailbone.views import View


log = logging.getLogger(__name__)


class FilemonView(View):
    """
    Misc. views for Filemon...(for now)
    """

    def restart(self):
        cmd = self.rattail_config.getlist('tailbone', 'filemon.restart', default='/bin/sleep 3') # simulate by default
        log.debug("attempting filemon restart with command: %s", cmd)
        try:
            subprocess.check_call(cmd)
        except Except as error:
            self.request.session.flash("FileMon daemon could not be restarted: {}".format(error), 'error')
        else:
            self.request.session.flash("FileMon daemon has been restarted.")
        return self.redirect(self.request.get_referrer(default=self.request.route_url('datasyncchanges')))

    @classmethod
    def defaults(cls, config):

        # fix permission group title
        config.add_tailbone_permission_group('filemon', label="FileMon")

        # restart filemon
        config.add_tailbone_permission('filemon', 'filemon.restart', label="Restart FileMon Daemon")
        config.add_route('filemon.restart', '/filemon/restart', request_method='POST')
        config.add_view(cls, attr='restart', route_name='filemon.restart', permission='filemon.restart')


def includeme(config):
    FilemonView.defaults(config)
