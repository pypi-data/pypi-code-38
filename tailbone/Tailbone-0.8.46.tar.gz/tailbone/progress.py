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
Progress Indicator
"""

from __future__ import unicode_literals, absolute_import

import os

from rattail.progress import ProgressBase

from beaker.session import Session


def get_progress_session(request, key, **kwargs):
    """
    Create/get a Beaker session object, to be used for progress.
    """
    id = '{}.progress.{}'.format(request.session.id, key)
    kwargs['use_cookies'] = False
    if kwargs.get('type') == 'file':
        kwargs['data_dir'] = os.path.join(request.rattail_config.appdir(), 'sessions')
    session = Session(request, id, **kwargs)
    return session


class SessionProgress(ProgressBase):
    """
    Provides a session-based progress bar mechanism.

    This class is only responsible for keeping the progress *data* current.  It
    is the responsibility of some client-side AJAX (etc.) to consume the data
    for display to the user.
    """

    def __init__(self, request, key, session_type=None):
        self.key = key
        self.session = get_progress_session(request, key, type=session_type)
        self.canceled = False
        self.clear()

    def __call__(self, message, maximum):
        self.clear()
        self.session['message'] = message
        self.session['maximum'] = maximum
        self.session['maximum_display'] = '{:,d}'.format(maximum)
        self.session['value'] = 0
        self.session.save()
        return self

    def clear(self):
        self.session.clear()
        self.session['complete'] = False
        self.session['error'] = False
        self.session['canceled'] = False
        self.session.save()

    def update(self, value):
        self.session.load()
        if self.session.get('canceled'):
            self.canceled = True
        else:
            self.session['value'] = value
            self.session.save()
        return not self.canceled
