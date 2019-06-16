# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Database Synchronization for Linux
"""

from __future__ import unicode_literals

from ...daemon import Daemon
from rattail.db.util import get_default_engine
from . import get_sync_engines, synchronize_changes


class SyncDaemon(Daemon):

    def run(self):
        remote_engines = get_sync_engines(self.config)
        if remote_engines:
            local_engine = get_default_engine(self.config)
            synchronize_changes(self.config, local_engine, remote_engines)


def get_daemon(config, pidfile=None):
    """
    Get a :class:`SyncDaemon` instance.
    """

    if pidfile is None:
        pidfile = config.get('rattail.db', 'sync.pid_path',
                             default='/var/run/rattail/dbsync.pid')
    daemon = SyncDaemon(pidfile)
    daemon.config = config
    return daemon


def start_daemon(config, pidfile=None, daemonize=True):
    """
    Start the database synchronization daemon.
    """

    get_daemon(config, pidfile).start(daemonize)


def stop_daemon(config, pidfile=None):
    """
    Stop the database synchronization daemon.
    """

    get_daemon(config, pidfile).stop()
