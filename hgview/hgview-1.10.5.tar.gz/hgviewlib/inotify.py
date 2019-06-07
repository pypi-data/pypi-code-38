# -*- coding: utf-8 -*-
# Copyright (c) 2003-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
"""
inotify support for hgview
"""

from os import read, path as osp
from time import sleep
from array import array
from fcntl import ioctl
from termios import FIONREAD
from struct import unpack, calcsize

from pyinotify import WatchManager

class Inotify(object):
    """Use inotify to get a file descriptor that shall be used into a main 
    loop.

    Constructor arguments:
    * repo - a mercurial repository object to watch
    * callback - callable called while processing events

    Use the ``process()`` method to update the display
    """

    def __init__(self, repo, callback=None):
        self.watchmanager = WatchManager()
        self._fd = self.watchmanager.get_fd()
        self.repo = repo
        self.callback = callback

    def update(self):
        '''update watchers'''
        # sorry :P. Import them here to reduce stating time
        from pyinotify import (IN_MODIFY, IN_ATTRIB, IN_MOVED_FROM, IN_MOVED_TO,
                               IN_DELETE_SELF, IN_MOVE_SELF, ALL_EVENTS,
                               IN_CLOSE_WRITE, IN_CREATE, IN_DELETE)
        mask = (IN_MODIFY | IN_ATTRIB | IN_MOVED_FROM | IN_MOVED_TO
                | IN_DELETE_SELF | IN_MOVE_SELF | IN_CLOSE_WRITE | IN_CREATE
                | IN_DELETE)
        self.watchmanager.add_watch(self.repo.root, mask,
                                    rec=True, auto_add=True,)

    def get_fd(self):
        """Return assigned inotify's file descriptor."""
        return self.watchmanager.get_fd()

    def read_events(self):
        """
        Read events and return related file name.
        """
        buf_ = array('i', [0])
        # get event queue size
        if ioctl(self._fd, FIONREAD, buf_, 1) == -1:
            return
        queue_size = buf_[0]
        try:
            # Read content from file
            raw = read(self._fd, queue_size)
        except Exception, msg:
            raise NotifierError(msg)
        rsum = 0  # counter

        data_fmt = 'iIII'
        data_size = calcsize(data_fmt)
        while rsum < queue_size:
            # Retrieve wd, mask, cookie and fname_len
            wd, mask, cookie, fname_len = unpack(data_fmt,
                                                 raw[rsum:rsum + data_size])
            # Retrieve name
            fname, = unpack('%ds' % fname_len,
                            raw[rsum + data_size:rsum + data_size + fname_len])
            end = fname.find('\x00')
            if end != -1:
                fname = fname[:end]
            rsum += data_size + fname_len
            yield fname

    def process(self):
        '''process events'''
        # Many events are raised for each modification on the repository
        # files or history (many files processed while committing, each file
        # processing may raises many event, e.g.IN_MODIFY and IN_ATTRIB.
        # We don't have to update the repository at each event. So, it may be a
        # good idea to put a delay during which the events are consumed, before
        # processing the callback.

        # Note: not implemented here, use the application mainloop to do so.

        # Note: I've try some other solutions, for instance: watching for
        # .hg/wlock or focusing on the manifests). But it seems that they
        # require a much more complicated implementation (update watched
        # files, fine watchers handling).
        # Finally, the current solution is simple, robust, and the end-user
        # interface seems to be good enough.

        # .hg/wlock means that some process is currently running on the
        # repository, so we have to sleep more. We can just return as another
        # event will be sent.
        if osp.exists(osp.join(self.repo.root or '', '.hg', 'wlock')):
            return
        # refresh viewer
        if self.callback:
            self.callback()

