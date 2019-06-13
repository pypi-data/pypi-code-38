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
Windows Services
"""

from __future__ import unicode_literals

import sys
import subprocess
import logging

try:
    import win32serviceutil
except ImportError:
    # Mock out for Linux.
    class Object(object):
        pass
    win32serviceutil = Object()
    win32serviceutil.ServiceFramework = Object

from rattail.config import make_config


log = logging.getLogger(__name__)


class Service(win32serviceutil.ServiceFramework):
    """
    Base class for Windows service implementations.
    """

    def __init__(self, args):
        """
        Constructor.
        """

        import win32event

        win32serviceutil.ServiceFramework.__init__(self, args)

        # Create "wait stop" event, for main worker loop.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def Initialize(self, config):
        """
        Service initialization.
        """
        return True

    def SvcDoRun(self):
        """
        This method is invoked when the service starts.
        """

        import win32service
        import win32event
        import servicemanager
        from pywintypes import error
        from winerror import ERROR_LOG_FILE_FULL

        # Write start occurrence to Windows Event Log.
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ''))
        except error as e:
            if e.winerror == ERROR_LOG_FILE_FULL:
                log.error("SvcDoRun: Windows event log is full!")
            else:
                raise

        # Read configuration file(s).
        logging.basicConfig()
        config = make_config(winsvc=self._svc_name_)
        config.configure_logging()

        # Figure out what we're supposed to be doing.
        if self.Initialize(config):

            # Wait infinitely for stop request, while threads do their thing.
            log.info("SvcDoRun: All threads started; waiting for stop request.")
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            log.info("SvcDoRun: Stop request received.")

        else: # Nothing to be done...
            msg = "Nothing to do!  (Initialization failed.)"
            log.warning("SvcDoRun: {0}".format(msg))
            servicemanager.LogWarningMsg(msg)
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # Write stop occurrence to Windows Event Log.
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, ''))
        except error as e:
            if e.winerror == ERROR_LOG_FILE_FULL:
                log.error("SvcDoRun: Windows event log is full!")
            else:
                raise

    def SvcStop(self):
        """
        This method is invoked when the service is requested to stop itself.
        """

        import win32service
        import win32event

        # Let the SCM know we're trying to stop.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # Let worker loop know its job is done.
        win32event.SetEvent(self.hWaitStop)


def execute_service_command(module, command, *args):
    """
    Execute a command for a Windows service.

    :param module: A proper Python module object, which must implement a
       command line interface when invoked directly by the Python interpreter.
       This interface is assumed to be implemented via the function
       ``win32serviceutil.HandleCommandLine()``.

    :param command: The name of a command supported by the service interface.
       This is presumably one of:

       * ``'install'``
       * ``'remove'``
       * ``'start'``
       * ``'stop'``
       * ``'restart'``

    :param \*args: If any additional arguments are present, they are assumed to
       be "option" arguments and will precede ``command`` when the actual
       command line is constructed.
    """
    command = [command]
    if args:
        command = list(args) + command
    subprocess.call([sys.executable, module.__file__] + command)


def delayed_auto_start_service(name):
    """
    Configure a Windows service for delayed automatic startup.

    :param name: The system-recognized name of the service (i.e. not the
       display name).

    .. note::
       It is assumed that the service is already configured to start
       automatically.  This function only modifies the service so that its
       automatic startup is delayed.
    """
    import win32service

    hSCM = win32service.OpenSCManager(
        None,
        None,
        win32service.SC_MANAGER_ENUMERATE_SERVICE)

    hService = win32service.OpenService(
        hSCM,
        name,
        win32service.SERVICE_CHANGE_CONFIG)

    win32service.ChangeServiceConfig2(
        hService,
        win32service.SERVICE_CONFIG_DELAYED_AUTO_START_INFO,
        True)

    win32service.CloseServiceHandle(hService)
    win32service.CloseServiceHandle(hSCM)
