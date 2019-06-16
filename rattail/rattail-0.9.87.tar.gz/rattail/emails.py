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
Common email config objects
"""

from __future__ import unicode_literals, absolute_import

import sys
import socket
from traceback import format_exception

import six

from rattail.mail import Email
from rattail.util import load_object
from rattail.core import Object
from rattail.time import make_utc, localtime


class datasync_error_watcher_get_changes(Email):
    """
    When any datasync watcher thread encounters an error trying to get changes,
    this email is sent out.
    """
    default_subject = "Watcher failed to get changes"

    def sample_data(self, request):
        from rattail.datasync import DataSyncWatcher
        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()
        watcher = DataSyncWatcher(self.config, 'test')
        watcher.consumes_self = True
        return {
            'watcher': watcher,
            'error': exc,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
            'datasync_url': '/datasyncchanges',
            'attempts': 2,
        }


class datasync_error_consumer_process_changes(Email):
    """
    When any datasync consumer thread encounters an error trying to process
    changes, this email is sent out.
    """
    default_subject = "Consumer failed to process changes"

    def sample_data(self, request):
        from rattail.datasync import DataSyncWatcher, DataSyncConsumer

        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()

        watcher = DataSyncWatcher(self.config, 'testwatcher')
        consumer = DataSyncConsumer(self.config, 'testconsumer')
        return {
            'watcher': watcher,
            'consumer': consumer,
            'error': exc,
            'attempts': 2,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
            'datasync_url': '/datasync/changes',
        }


class filemon_action_error(Email):
    """
    When any filemon thread encounters an error (and the retry attempts have
    been exhausted) then it will send out this email.
    """
    default_subject = "Error invoking action(s)"

    def sample_data(self, request):
        from rattail.filemon import Action
        action = Action(self.config)
        action.spec = 'rattail.filemon.actions:Action'
        action.retry_delay = 10
        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()
        return {
            'hostname': socket.gethostname(),
            'path': '/tmp/foo.csv',
            'action': action,
            'attempts': 3,
            'error': exc,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
        }


class ImporterEmail(Email):
    """
    Sent when a "version catch-up" import is performed, which involves changes.
    """
    abstract = True
    fallback_key = 'rattail_import_updates'
    handler_spec = None

    def get_handler(self, config):
        return load_object(self.handler_spec)(config)

    def sample_data(self, request):
        handler = self.get_handler(request.rattail_config)
        obj = Object()
        local_data = {
            'foo': 42,
            'bar': True,
            'baz': 'something',
        }
        host_data = {
            'foo': 42,
            'bar': False,
            'baz': 'something else',
        }
        return {
            'host_title': handler.host_title,
            'local_title': handler.local_title,
            'runtime': "1 second",
            'argv': ['bin/rattail', 'import-something'],
            'changes': {
                'Widget': (
                    [],                             # created
                    [(obj, local_data, host_data)], # updated
                    [],                             # deleted
                ),
            },
            'render_record': lambda x: six.text_type(x),
            'max_display': 15,
        }


class rattail_import_versions_updates(Email):
    """
    Sent when a "version catch-up" import is performed, which involves changes.
    """
    fallback_key = 'rattail_import_updates'
    default_subject = "Changes for Rattail -> Rattail (Versions) import"


class upgrade_failure(Email):
    """
    Sent when an app upgrade is attempted, but ultimately failed.
    """
    default_subject = "Upgrade Failure"

    def sample_data(self, request):
        upgrade = Object(
            description="upgrade to the latest!",
            notes="nothing special",
            executed=make_utc(),
            executed_by="Fred Flintstone",
            exit_code=42,
        )
        return {
            # TODO: first 3 args should be provided by some common logic instead...
            'rattail_config': self.config,
            'localtime': localtime,
            'app_title': self.config.app_title(),
            'upgrade': upgrade,
            'upgrade_url': '#',
        }


class upgrade_success(Email):
    """
    Sent when an app upgrade is performed successfully.
    """
    default_subject = "Upgrade Success"

    def sample_data(self, request):
        upgrade = Object(
            description="upgrade to the latest!",
            notes="nothing special",
            executed=make_utc(),
            executed_by="Fred Flintstone",
            exit_code=0,
        )
        return {
            # TODO: first 3 args should be provided by some common logic instead...
            'rattail_config': self.config,
            'localtime': localtime,
            'app_title': self.config.app_title(),
            'upgrade': upgrade,
            'upgrade_url': '#',
        }


class user_feedback(Email):
    """
    Sent when a user submits a Feedback form from the web UI.
    """
    default_subject = "User Feedback"

    def sample_data(self, request):
        return {
            'user': None,
            'user_name': "Fred Flintstone",
            'referrer': request.route_url('home'),
            'client_ip': '127.0.0.1',
            'message': "Hey there,\n\njust wondered what the heck was going on with this site?  It's crap.\n\nFred",
        }
