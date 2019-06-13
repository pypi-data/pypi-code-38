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
File Monitor Actions
"""

from __future__ import unicode_literals, absolute_import

import os
import sys
import time
from six.moves import queue
import socket
import subprocess
import logging
from traceback import format_exception

from rattail.mail import send_email


log = logging.getLogger(__name__)


class Action(object):
    """
    Base class for file monitor actions.
    """

    def __init__(self, config):
        self.config = config

    def __call__(self, *args, **kwargs):
        """
        This method must be implemented in the subclass; it defines what the
        action actually *does*.  The file monitor will invoke this method for
        all new files which are discovered.
        """
        raise NotImplementedError


class CommandAction(Action):
    """
    Simple file monitor action which can execute a command as a subprocess.
    """

    def __init__(self, config, cmd):
        self.config = config
        self.cmd = cmd

    def __call__(self, path):
        """
        Run the requested command.
        """
        cmd = self.cmd.format(
            path=path,
            filename=os.path.basename(path))
        subprocess.check_call(cmd, shell=True)


class StopProcessing(Exception):
    """
    Simple exception to indicate action processing should stop.  This is really
    only useful for tests.
    """


def perform_actions(profile):
    """
    Target for action threads.  Provides the main loop which checks the queue
    for new files and invokes actions for each, as they appear.
    """

    # If running on Windows, we add a step to help ensure the file is truly
    # free of competing process interests.  (In fact it would be nice to have
    # this on Linux as well, but I'm not sure how to do it there.)
    wait_for_file = lambda p: p
    if sys.platform.startswith(u'win'): # pragma: no cover
        import win32api
        from rattail.win32 import file_is_free
        def wait_for_file(path):
            while not file_is_free(path):
                win32api.Sleep(0)

    stop = False
    while not stop:

        # Suspend execution briefly, to avoid consuming so much CPU...
        time.sleep(0.01)

        try:
            path = profile.queue.get_nowait()
        except queue.Empty:
            pass
        except StopProcessing:
            stop = True
        else:
            log.debug(u"queue contained a file: {0}".format(repr(path)))

            # In some cases, processing one file may cause other related files
            # to also be processed.  When this happens, a path on the queue may
            # point to a file which no longer exists.
            if not os.path.exists(path):
                log.warning(u"file path does not exist: {0}".format(path))
                continue

            # This does nothing unless running on Windows.
            wait_for_file(path)

            for action in profile.actions:
                try:
                    invoke_action(action, path)

                except:
                    # Stop processing files altogether for this profile if it
                    # is so configured.
                    if profile.stop_on_error:
                        log.warning(u"an error was encountered, and configuration dictates that no more "
                                    u"actions will be processed for profile {0}".format(repr(profile.key)))
                        stop = True

                    # Either way no more actions should be invoked for this
                    # particular file.
                    break


def invoke_action(action, path):
    """
    Invoke a single action on a file, retrying as necessary.
    """
    attempts = 0
    errtype = None
    while True:
        attempts += 1
        log.debug(u"invoking action {0} (attempt #{1} of {2}) on file: {3}".format(
                repr(action.spec), attempts, action.retry_attempts, repr(path)))

        try:
            action.action(path, *action.args, **action.kwargs)

        except Exception as error:

            # If we've reached our final attempt, stop retrying.
            if attempts >= action.retry_attempts:
                log.debug("attempt #{} failed for action '{}' (giving up) on "
                          "file: {}".format(attempts, action.spec, path),
                          exc_info=True)
                exc_type, exc, traceback = sys.exc_info()
                send_email(action.config, 'filemon_action_error', {
                    'hostname': socket.gethostname(),
                    'path': path,
                    'action': action,
                    'attempts': attempts,
                    'error': exc,
                    'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
                })
                raise

            # If this exception is not the first, and is of a different type
            # than seen previously, do *not* continue to retry.
            if errtype is not None and not isinstance(error, errtype):
                log.exception(u"new exception differs from previous one(s), giving up on "
                              u"action {0} for file: {1}".format(repr(action.spec), repr(path)))
                raise

            # Record the type of exception seen, and pause for next retry.
            log.warning(u"attempt #{0} failed for action {1} on file: {2}".format(
                    attempts, repr(action.spec), repr(path)), exc_info=True)
            errtype = type(error)
            log.debug(u"pausing for {0} seconds before making attempt #{1} of {2}".format(
                    action.retry_delay, attempts + 1, action.retry_attempts))
            if action.retry_delay:
                time.sleep(action.retry_delay)

        else:
            # No error, invocation successful.
            log.debug(u"attempt #{0} succeeded for action {1} on file: {2}".format(
                    attempts, repr(action.spec), repr(path)))
            break


def raise_exception(path, message=u"Fake error for testing"):
    """
    File monitor action which always raises an exception.

    This is meant to be a simple way to test the error handling of a file
    monitor.  For example, whether or not file processing continues for
    subsequent files after the first error is encountered.  If logging
    configuration dictates that an email should be sent, it will of course test
    that as well.
    """
    raise Exception(u'{0}: {1}'.format(message, path))


def noop(path):
    """
    File monitor action which does nothing at all.

    This exists for the sake of tests.  I doubt it's useful in any other
    context.
    """
