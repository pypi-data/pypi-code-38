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
Console Stuff
"""

from __future__ import unicode_literals, absolute_import

import os
import sys
import json
import socket

import six
from progress.bar import Bar


class ProgressBase(object):
    """
    Base class for all progress implementations.
    """

    def __init__(self, message, maximum):
        self.message = message
        self.maximum = maximum

    def update(self, value):
        return True

    def finish(self):
        pass

    def destroy(self):
        self.finish()


class ConsoleProgress(ProgressBase):
    """
    Provides a console-based progress bar.
    """

    def __init__(self, message, maximum, stdout=None):
        self.stdout = stdout or sys.stderr
        self.stdout.write("\n{}...\n".format(message))
        self.bar = Bar(message='', max=maximum, width=70,
                       suffix='%(index)d/%(max)d %(percent)d%% ETA %(eta)ds')

    def update(self, value):
        self.bar.next()
        return True

    def finish(self):
        self.bar.finish()


class FileProgress(ProgressBase):
    """
    Progress indicator which writes progress info to the given file object.
    """

    def __init__(self, path):
        self.path = path

    def __call__(self, message, maximum):
        self.message = message
        self.maximum = maximum
        self.value = 0
        self.write_info()
        return self

    def write_info(self):
        info = {
            'message': self.message,
            'maximum': self.maximum,
            'value': self.value,
        }
        with open(self.path, 'wt') as f:
            f.write(json.dumps(info))
            f.flush()

    def update(self, value):
        self.value = value
        self.write_info()
        return True

    def finish(self):
        if os.path.exists(self.path):
            os.remove(self.path)


class SocketProgress(ProgressBase):
    """
    Progress indicator which writes progress info to the given socket object.
    """

    def __init__(self, host, port, suffix=None):
        self.host = host
        self.port = port
        if suffix:
            self.suffix = suffix
        else:
            self.suffix = "\n\n.".encode('utf_8')

    def __call__(self, message, maximum):
        self.connection = socket.create_connection((self.host, self.port))
        self.message = message
        self.maximum = maximum
        self.value = 0
        self.write_progress()
        return self

    def write_data(self, data):
        data = json.dumps(data)
        if six.PY3:
            data = data.encode('utf_8')
        self.connection.send(data)
        self.connection.send(self.suffix)

    def write_progress(self):
        self.write_data({
            'message': self.message,
            'maximum': self.maximum,
            'value': self.value,
        })

    def update(self, value):
        self.value = value
        self.write_progress()
        return True

    def finish(self):
        self.write_data({
            'process_complete': True,
        })
        self.connection.close()
