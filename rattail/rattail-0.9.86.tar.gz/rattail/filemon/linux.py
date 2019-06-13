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
File Monitor for Linux
"""

from __future__ import unicode_literals, absolute_import

from six.moves import queue
import logging

import pyinotify

from rattail.daemon import Daemon
from rattail.threads import Thread
from rattail.filemon.config import load_profiles
from rattail.filemon.actions import perform_actions
from rattail.filemon.util import queue_existing


log = logging.getLogger(__name__)


class EventHandler(pyinotify.ProcessEvent):
    """
    Event processor for file monitor daemon.  This receives notifications of
    file system events, and places new files on the queue as appropriate.
    """

    def my_init(self, profile=None, **kwargs):
        self.profile = profile

    def process_IN_ACCESS(self, event):
        log.debug(u"IN_ACCESS: {0}".format(event.pathname))

    def process_IN_ATTRIB(self, event):
        log.debug(u"IN_ATTRIB: {0}".format(event.pathname))

    def process_IN_CLOSE_WRITE(self, event):
        log.debug(u"IN_CLOSE_WRITE: {0}".format(event.pathname))
        if not self.profile.watch_locks:
            self.profile.queue.put(event.pathname)

    def process_IN_CREATE(self, event):
        log.debug(u"IN_CREATE: {0}".format(event.pathname))

    def process_IN_DELETE(self, event):
        log.debug(u"IN_DELETE: {0}".format(event.pathname))
        if self.profile.watch_locks and event.pathname.endswith(u'.lock'):
            self.profile.queue.put(event.pathname[:-5])

    def process_IN_MODIFY(self, event):
        log.debug(u"IN_MODIFY: {0}".format(event.pathname))

    def process_IN_MOVED_TO(self, event):
        log.debug(u"IN_MOVED_TO: {0}".format(event.pathname))
        if not self.profile.watch_locks:
            self.profile.queue.put(event.pathname)


class FileMonitorDaemon(Daemon):
    """
    Linux daemon implementation of the File Monitor.
    """

    def run(self):

        watch_manager = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(watch_manager)

        mask = (pyinotify.IN_ACCESS
                | pyinotify.IN_ATTRIB
                | pyinotify.IN_CLOSE_WRITE
                | pyinotify.IN_CREATE
                | pyinotify.IN_DELETE
                | pyinotify.IN_MODIFY
                | pyinotify.IN_MOVED_TO)

        monitored = load_profiles(self.config)
        for key, profile in monitored.items():

            # Create a file queue for the profile.
            profile.queue = queue.Queue()

            # Perform setup for each of the watched folders.
            for path in profile.dirs:

                # Maybe put all pre-existing files in the queue.
                if profile.process_existing:
                    queue_existing(profile, path)

                # Create a watch for the folder.
                log.debug(u"adding watch to profile '{0}' for folder: {1}".format(key, path))
                watch_manager.add_watch(path, mask, proc_fun=EventHandler(profile=profile))

            # Create an action thread for the profile.
            name = u'actions-{0}'.format(key)
            log.debug(u"starting action thread: {0}".format(name))
            thread = Thread(target=perform_actions, name=name, args=(profile,))
            thread.daemon = True
            thread.start()

        # Fire up the watchers.
        notifier.loop()


def get_daemon(config, pidfile=None):
    """
    Get a :class:`FileMonitorDaemon` instance.
    """
    if pidfile is None:
        pidfile = config.get('rattail.filemon', 'pid_path',
                             default='/var/run/rattail/filemon.pid')
    return FileMonitorDaemon(pidfile, config=config)


def start_daemon(config, pidfile=None, daemonize=True):
    """
    Start the file monitor daemon.
    """
    get_daemon(config, pidfile).start(daemonize)


def stop_daemon(config, pidfile=None):
    """
    Stop the file monitor daemon.
    """
    get_daemon(config, pidfile).stop()
