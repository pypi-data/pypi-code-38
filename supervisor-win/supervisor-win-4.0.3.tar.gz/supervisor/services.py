# coding=utf-8
"""
Installation script for the supervisor as a service
To install the service on a terminal, as an administrator, run the command line:
python -m supervisor.services install -c "{path}\supervisord.conf"
"""
from __future__ import print_function

import argparse
import logging.handlers
import os
import re
import servicemanager
import socket
import sys
import traceback
import win32event
import win32service

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    import _winreg as winreg
except ImportError:
    import winreg

import win32serviceutil

# supervisor{dir}/supervisor{package}
LOCAL_DIR = os.path.dirname(__file__)

# removes supervisor package directory from path
local_path_index = None
for index, path in enumerate(sys.path):
    if re.match(re.escape(path), LOCAL_DIR, re.U | re.I):
        local_path_index = index
        break
if local_path_index is not None:
    sys.path.pop(local_path_index)

try:
    import supervisor
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(LOCAL_DIR, '..')))

SUPERVISOR_PREFIX = "Supervisor Pyv{0.winver}".format(sys)


class ConfigReg(object):
    """Saves the path to the supervisor.conf in the system registry"""
    prefix = SUPERVISOR_PREFIX

    def __init__(self, prefix=None):
        self.software_key = winreg.OpenKey(winreg.HKEY_CURRENT_CONFIG, "Software")
        if prefix is not None:
            self.prefix = prefix
        self.service_name_key = self.prefix + " Service"
        self.config_name_key = "Config"

    def set(self, filepath):
        with winreg.CreateKey(self.software_key, self.service_name_key) as srv_key:
            winreg.SetValue(srv_key, self.config_name_key, winreg.REG_SZ, filepath)

    def get(self):
        with winreg.OpenKey(self.software_key, self.service_name_key) as srv_key:
            value = winreg.QueryValue(srv_key, self.config_name_key)
        return value

    def close(self):
        """cleanup"""
        winreg.CloseKey(self.software_key)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


class SupervisorService(win32serviceutil.ServiceFramework):
    _svc_name_ = SUPERVISOR_PREFIX
    _svc_display_name_ = "{0} process monitor".format(SUPERVISOR_PREFIX)
    _svc_description_ = "A process control system"
    _svc_deps_ = []

    _exe_name_ = sys.executable
    _exe_args_ = '"' + os.path.abspath(sys.argv[0]) + '"'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

        # Gets the path of the registry configuration file
        try:
            with ConfigReg() as reg:
                self.config_filepath = reg.get()
        except WindowsError:
            config_reg_exc = traceback.format_exc()
            self.config_filepath = None
        else:
            config_reg_exc = None

        # The log goes to the location of the configuration file
        if self.config_filepath is not None:
            config_dir = os.path.dirname(self.config_filepath)
        else:  # or to python home
            config_dir = os.getcwd()

        self.logger = logging.getLogger(__name__)
        log_path = os.path.join(config_dir, SUPERVISOR_PREFIX.lower() + "-service.log")
        hdl = logging.handlers.RotatingFileHandler(log_path,
                                                   maxBytes=1024 ** 2,
                                                   backupCount=3)
        hdl.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(hdl)
        self.logger.info("supervisor config path: {0!s}".format(self.config_filepath))

        if config_reg_exc is not None:
            self.logger.error("* The service needs to be reinstalled")
            self.logger.error(config_reg_exc)
            logging.shutdown()
            exit(-1)

    # noinspection PyBroadException
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # Supervisor process stop event
        try:
            self.logger.info("supervisorctl shutdown")
            from supervisor import supervisorctl
            stdout = StringIO()
            supervisorctl.main(("-c", self.config_filepath, "shutdown"),
                               stdout=stdout)
            self.logger.info(stdout.getvalue().strip("\n "))
        except:
            self.logger.exception("supervisorctl shutdown execution failed")
        finally:
            logging.shutdown()
            win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    # noinspection PyBroadException
    def main(self):
        """Starts running the supervisor"""
        try:
            from supervisor import supervisord
            self.logger.info("supervisor starting...")
            supervisord.main(("-c", self.config_filepath))
        except:
            self.logger.exception("supervisor starting failed")


def parse_args_config(options, argv):
    args = []
    index = 0
    while True:
        try:
            item = argv[index]
        except IndexError:
            break
        for opts in options:
            if any(filter(item.startswith, opts['args'])):
                name = argv.pop(index)
                if name.find('=') > -1:
                    args.extend(item.split('='))
                    index -= 1
                    continue
                args.append(name)
                kwargs = opts.setdefault('kwargs', {})
                if kwargs.get('required', False):
                    try:
                        args.append(argv.pop(index))
                        index -= 1
                    except IndexError:
                        continue
                else:
                    index -= 1
        index += 1
    return args


def get_config_args(argv=None):
    argv = list(sys.argv) if argv is None else list(argv)
    options = [
        {'args': ('-h', '--help'),
         'kwargs': {'required': False,
                    'action': 'store_true'}},
        {'args': ('-c', '--config'),
         'kwargs': {'type': argparse.FileType('r'),
                    'help': 'full filepath to supervisor.conf',
                    'required': 'install' in argv}}
    ]
    args = parse_args_config(options, argv)
    return options, args, argv


def main():
    # starts in the main python directory.
    os.chdir(os.path.dirname(sys.executable))

    if len(sys.argv) == 1:
        # service must be starting...
        # for the sake of debugging etc, we use win32traceutil to see
        # any unhandled exceptions and print statements.
        print("supervisor service is starting...")
        print("(execute this script with '--help' if that isn't what you want)")
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SupervisorService)
        # Now ask the service manager to fire things up for us...
        servicemanager.StartServiceCtrlDispatcher()
        print("supervisor service done!")
    else:
        # file configuration supervisord.conf
        options, args, srv_argv = get_config_args(sys.argv[1:])
        # print(args, srv_argv, sep='\n')
        parser = argparse.ArgumentParser(add_help=False)
        for opts in options:
            parser.add_argument(*opts['args'], **opts.get('kwargs', {}))
        options = parser.parse_args(args=args)
        if options.config:
            try:
                options.config.close()
            except OSError:
                pass
        if options.help:
            parser.print_help(file=sys.stdout)
            print()
            srv_argv.append('-h')
        elif options.config:
            with ConfigReg() as reg:
                reg.set(options.config.name)
        srv_argv.insert(0, sys.argv[0])
        win32serviceutil.HandleCommandLine(SupervisorService, argv=srv_argv)


if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        raise
    except:
        print(" command execution failed ".center(35, '='))
        traceback.print_exc(limit=3)
