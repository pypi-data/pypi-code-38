"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""
import base
import datetime
import importlib
import os
import psutil
import requests
import sys
import time
import multiprocessing as multi
import gateway_helpers
from base import BaseClient, logger

import settings

os.environ['NO_PROXY'] = 'gradientone.com'
os.environ['no_proxy'] = 'gradientone.com'
COMMON_SETTINGS = settings.COMMON_SETTINGS
CLIENT_SETTINGS = settings.CLIENT_SETTINGS
BASE_URL = settings.BASE_URL

UPDATE_CHECK_INTERVAL = 10
DEFAULT_PYTHONPATH = '/usr/local/lib/python2.7/dist-packages'
TMPDIR = settings.TMPDIR
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


class ClientProcess(multi.Process):
    def __init__(self, *args, **kwargs):
        super(ClientProcess, self).__init__(*args, **kwargs)
        self.child_processes = []
        self.child_pids = []
        self.my_pid = None

        self._is_unit_test = False
        self._is_integration_test = False

    @property
    def is_unit_test(self):
        """For testing client classes"""
        return self._is_unit_test

    @property
    def is_integration_test(self):
        """For testing client classes with server app"""
        return self._is_integration_test

    def terminate(self):
        logger.warning("ClientProcess terminate() for %s" % self.pid)
        kill_proc_tree(self.pid)
        try:
            logger.warning("super(ClientProcess, self).terminate()")
            super(ClientProcess, self).terminate()
        except Exception as e:
            logger.warning("Exc Process.terminate() %s" % e)


class BaseController(ClientProcess, BaseClient):
    def __init__(self, target=None, name="", keep_alive_interval=600,
                 *args, **kwargs):
        """Initializes the BaseController

        target - the target function for the process this controller
            is managing. Every target function needs to take the
            ClientInfo as the first argument

        name - A client needs to have some identifier that labels it so
            that the controller knows what to start, stop, restart, and
            check for activity. The 'name' should be unique to each
            client. While similar in purpose to pid, the 'name' is
            different in that the same name will be used for each
            restart of a given client, despite new pids being generated
            each time. The 'name' is different from Unix process name
            in that the names here for each client should be unique,
            whereas Unix process names are not. There's no validation
            being done on these names being used, so if you use the
            same name for two different clients in your code you
            will see some strange behavior.

        keep_alive_interval - seconds that target must update the
            activity file within, else this controller will restart
            the target process.
        """
        super(BaseController, self).__init__(*args, **kwargs)
        self.target = target
        self.name = name
        self.keep_alive_interval = keep_alive_interval
        self.session = requests.session()
        self.session.headers.update(base.get_headers())
        self.skip_http_reqs = False  # for local only testing/debugging

    def read(self, file):
        """Helper function for reading activity files

        If no file, writes current time and returns the time string
        """
        if not os.path.isfile(file):
            c_time = datetime.datetime.now()
            fmt = DATETIME_FORMAT
            time_string = c_time.strftime(fmt)
            with open(file, 'w') as f:
                f.write(time_string)
                return time_string
        with open(file, 'r') as f:
            return f.read()

    def write(self, file, content):
        with open(file, 'w') as f:
            f.write(content)

    def start_process(self, target, name, ps_args=(), ps_kwargs={}):
        """Starts a process and saves its pid

        The pid is written to a file, named with the 'name' arg,
        <name>.pid, so with the simple example it's simple.txt.

        The 'name' is used for the Process, the pid file, and the
        activity file relating to the process for the function. The
        convention is <name>_activity.txt, so with the simple example
        this is simple_activity.txt.

        """
        file_counter = 0
        logger.info("%s controller is starting process '%s'"
                    % (self.name, name))
        if sys.platform == 'win32':
            multi.freeze_support()
        ps = ClientProcess(target=target, name=name,
                           args=ps_args, kwargs=ps_kwargs)

        ps.start()
        self.child_processes.append(ps)
        self.child_pids.append(ps.pid)
        ps.my_pid = ps.pid
        pidfile = os.path.join(TMPDIR, name + ".pid")

        logger.info("Writing pid %s to file %s" % (ps.pid, pidfile))
        base.safe_write(pidfile, str(ps.pid), file_counter)

        logger.info("%s controller's child pids: %s"
                    % (self.name, self.child_pids))
        gateway_helpers.save_pid(ps.pid)
        return ps.pid

    def stop_process(self, pid=None):
        """Stops the controllers target child process"""
        if pid:
            kill_proc_tree(pid)
            return
        # if not target pid, kill all child pids of current ps
        logger.info("STOPPING!!!! pid and type %s %s"
                    % (self.my_pid, type(self.my_pid)))
        kill_proc_tree(self.my_pid)
        return

    def restart_process(self, target, name, ps_args=(), pid=""):
        """Stops and starts the client process given a func and name

        The 'name' is used for the Process, the pid file, and the
        activity file relating to the process for the function.
        """
        if not pid:
            pid = self.get_pid_from_name(name)
        if not pid:
            return None
        logger.info("Restarting process %s..." % name)
        self.stop_process(pid=pid)
        self.start_process(target, name=name, ps_args=ps_args)

    def if_active_pid(self, pid):
        """Check if active unix pid."""
        if psutil.pid_exists(pid):
            return True
        else:
            logger.info("The process with pid %s does not exist" % pid)
            return False

    def get_pid_from_name(self, name):
        """Returns the pid for a given client process name.

        The method will check the pid file for the name
        """
        try:
            pid_file = os.path.join(TMPDIR, name + ".pid")
            with open(pid_file, 'r') as f:
                pid = int(f.read())
                logger.info("Read pid %s from file %s" % (pid, pid_file))
                return pid
        except Exception as e:
            logger.warning("get_pid_from_name exception: %s" % e)
            return None


class ClientInfo(object):
    """Keeps track of basic client process info"""
    def __init__(self, target=None, name="", keep_alive_interval=600, pid="",
                 command_queue=None, identity_dict={}):
        """Intializes ClientInfo object

        Rule: If a client process doesn't update the activity file for
            its process within the keep_alive_interval, this method
            will restart the client process. Otherwise, if the client
            process is behaving normally and updating the activity
            file within the required keep_alive_interval, this method
            will log the new activity update from the sub client.

        target - the process that this method is starting and keeping
            alive. This method will pass kwargs 'keep_alive_interval'
            and 'activity_file' for this target process to use to be
            sure to update the activity file within the
            keep_alive_interval.

        name - the name used to keep track of the target process

        keep_alive_interval - the seconds allowed to pass between
            updates to the activity file. If no update is made within
            the keep_alive_interval, this method will restart the
            target process.

        pid - the pid of the client process

        activity_file - the file that needs to be periodically updated
            for keep_alive checks

        identity_dict - a dictionary containing identity information
            about this client. Typically this is the instrument
            identity data with instrument_type, address, etc.
        """
        self.target = target
        self.name = name
        self.keep_alive_interval = keep_alive_interval
        self.pid = pid
        self.command_queue = command_queue
        self.activity_file = os.path.join(TMPDIR, name + '_activity.txt')
        self.identity_dict = identity_dict

    @property
    def active(self):
        """If the client process is active or not"""
        if psutil.pid_exists(self.pid):
            return True
        else:
            return False


class SimpleClient(object):
    def run_example(self, sec_btw_simple_prints=5, activity_file=""):
        """Run example simple client

        If sec_btw_simple_prints is less than the keep_alive_interval,
        that is to say it prints and updates the activity more
        frequently than required by the keep_alive_interval, it will
        simply continue to print indefinitely.

        Else if the sec_btw_simple_prints is greater than the
        keep_alive_interval of the client controller then the
        controller will restart this client. A restart will stop
        this process and start a new process calling this same
        method.
        """
        if not activity_file:
            activity_file = "simple_activity.txt"
        while True:
            msg = "SimpleClient: run at %s" % str(datetime.datetime.now())
            logger.info(msg)
            with open(activity_file, 'w') as f:
                f.write(msg)
            time.sleep(sec_btw_simple_prints)


class SimpleController(BaseController):
    """A controller for examples

        When kickoff() is called by an instance of SimpleController, the
    SimpleClient is run within a keep alive loop. See the
    BaseController kickoff() method for more details
    """
    def __init__(self, *args, **kwargs):
        simple = SimpleClient()
        self.target = simple.run_example
        self.name = 'simple'


class ModuleHelper(object):

    def __init__(self, pkg_name='gradientone'):
        self.client_module = self.get_module(pkg_name)

    def get_module(self, module_name):
        if module_name in sys.modules:
            return sys.modules[module_name]
        else:
            return importlib.import_module(module_name)


def run_example():
    ctrl = SimpleController()
    ctrl.start()


def kill_proc_tree(pid=None, exc_pid=None, all_client_ps=False,
                   children_only=False):
    """Kills processes in process tree

    Args:
        pid: the specified pid to kill or pid of parent process
        exc_pid: the pid to except from killing, or leave it be
        all_client_ps: goes through known client pids and kills those processe
        children_only: kills just the child processes of the specified pid,
            requires the pid kwarg to be specified.
    """
    if all_client_ps:
        # Go through the client pid list
        pid_list = gateway_helpers.get_pid_list()
        for pid in pid_list:
            if pid == exc_pid:
                continue
            if not check_pid(pid):
                continue
            logger.info("Killing pid %s" % pid)
            try:
                ps = psutil.Process(pid)
                ps.kill()
                ps.wait(5)
            except Exception as e:
                logger.warning(e, exc_info=True)

        # If no specific pid given, that's it
        if not pid:
            return

    # Otherwise, kill the specified process and all child processes
    try:
        if not check_pid(pid):
            logger.info("No process for pid %s (nothing to kill)" % pid)
            return
        logger.warning("Killing process tree for pid %s" % pid)
        specified_process = psutil.Process(pid)
        children = specified_process.children(recursive=True)
        for child in children:
            if not check_pid(child.pid):
                continue
            logger.warning("Killing child pid %s" % child.pid)
            child.kill()
        psutil.wait_procs(children, timeout=5)
        if not children_only:
            specified_process.kill()
            specified_process.wait(5)
    except Exception as e:
        logger.warning(e, exc_info=True)


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True
