# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the Tensorboard class and related utilities to launch a Tensorboard server."""
from concurrent.futures import ThreadPoolExecutor
from azureml._run_impl.run_watcher import RunWatcher
from azureml._history.utils.constants import LOGS_DIR
import tempfile
from threading import Event, Thread
from subprocess import Popen, PIPE
import os
from requests import Session
import logging
import time
import re
import sys

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

module_logger = logging.getLogger(__name__)


class Tensorboard(object):
    """Represents a Tensorboard instance tied to one or more Runs."""

    LOGS_ARTIFACT_PREFIX = os.path.normpath(LOGS_DIR) + "/"

    def __init__(self, runs, local_root=None, port=6006):
        """
        Initialize the tensorboard server.

        :param runs: One or more runs to attach to this Tensorboard instance.
        :type runs: azureml.core.run.Run | list[azureml.core.run.Run]
        :param local_root: An optional local directory to store the run logs in.
        :type local_root: str
        :param port: The port to run this Tensorboard instance on.
        :type port: int
        """
        if local_root is None:
            local_root = tempfile.mkdtemp()
        if type(runs) is not list:
            runs = [runs]
        self._runs = runs
        self._local_root = local_root
        self._run_watchers = None
        self._tb_proc = None
        self._job_handle = None
        self._executor = None
        self._event = None
        self._port = port
        self._session = None

    def start(self):
        """
        Start the Tensorboard instance, and begin downloading data for the runs.

        :return: The URL returned by the Tensorboard instance.
        :rtype: str
        """
        if self._tb_proc is not None:
            module_logger.debug("Start called but we already have a TB process")
            return

        self._executor = ThreadPoolExecutor()
        self._event = Event()
        self._session = Session()

        # Make a run watcher for each run we are monitoring
        self._run_watchers = list(map(
            lambda r: RunWatcher(
                r,
                # each run should go in its own subdirectory
                # TODO: should we add child runs somehow?
                local_root=os.path.join(self._local_root, r.id),
                remote_root=Tensorboard.LOGS_ARTIFACT_PREFIX,
                executor=self._executor,
                event=self._event,
                session=self._session),
            self._runs))
        for w in self._run_watchers:
            self._executor.submit(w.refresh_requeue)

        # We use sys.executable here to ensure that we can import modules from the same environment
        # as the current process.
        # (using just "python" results in the global environment, which might not have a Tensorboard module)
        # sometimes, sys.executable might not give us what we want (i.e. in a notebook), and then we just have to hope
        # that "python" will give us something useful
        python_binary = sys.executable or "python"
        self._tb_proc = Popen(
            [python_binary, "-m", "tensorboard.main",
             "--logdir", self._local_root,
             "--port", str(self._port)],
            stderr=PIPE, stdout=PIPE, universal_newlines=True)
        if os.name == "nt":
            self._win32_kill_subprocess_on_exit(self._tb_proc)

        url = self._wait_for_url()
        # in notebooks, this shows as a clickable link (whereas the returned value is not parsed in output)
        print(url)
        return url

    def _win32_kill_subprocess_on_exit(self, child):
        """
        Tie a process's lifetime to this process's on Windows.

        (i.e. kill it when we exit)
        :param child: The process to tie to this one.
        :type child: Popen
        :return: None
        """
        try:
            import win32api
            import win32con
            import win32job

            h_job = win32job.CreateJobObject(None, "")
            extended_info = win32job.QueryInformationJobObject(h_job, win32job.JobObjectExtendedLimitInformation)
            extended_info['BasicLimitInformation']['LimitFlags'] = win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            win32job.SetInformationJobObject(h_job, win32job.JobObjectExtendedLimitInformation, extended_info)

            # Convert process id to process handle
            perms = win32con.PROCESS_TERMINATE | win32con.PROCESS_SET_QUOTA
            h_process = win32api.OpenProcess(perms, False, child.pid)

            win32job.AssignProcessToJobObject(h_job, h_process)
            # We need to hold this handle to the job now, or it will die prematurely
            self._job_handle = h_job
        except ImportError:
            module_logger.warning("'pywin32' package not found. Please install this package" +
                                  " in order to ensure process cleanup." +
                                  " Otherwise, make sure to stop your Tensorboard instance.")
        except Exception as ex:
            module_logger.warning("Unable to tie child process lifetime to this process, {}".format(ex))

    def _get_url(self, line):
        # if it's a managed notebook, create the url from local file
        notebook_vm_url = self._get_url_from_notebook_vm()
        if notebook_vm_url:
            return notebook_vm_url

        # else, return the url the traditional way
        m = re.search(r"(https?://.*?)\s", line)
        # Tensorflow helpfully directs the user to their own website if there are issues loading it.
        # So, make sure we don't presume success if we see that URL.
        if m and "tensorflow.org" not in m.group(1):
            return m.group(1)
        return None

    def _get_url_from_notebook_vm(self):
        nbvm_file_path = "/mnt/azmnt/.nbvm"
        if not (os.path.exists(nbvm_file_path) and os.path.isfile(nbvm_file_path)):
            return None

        envre = re.compile(r'''^([^\s=]+)=(?:[\s"']*)(.+?)(?:[\s"']*)$''')
        result = {}
        with open(nbvm_file_path) as nbvm_variables:
            for line in nbvm_variables:
                match = envre.match(line)
                if match is not None:
                    result[match.group(1)] = match.group(2)

        if "instance" not in result or "domainsuffix" not in result:
            return None

        instance_name = result["instance"]
        domain_suffix = result["domainsuffix"]
        return "https://{}-6006.{}".format(instance_name, domain_suffix)

    # Machinery to read a pipe without blocking.
    # This makes me very sad.
    def _wait_for_url(self, timeout=60):
        def enqueue_output(out, q):
            for l in iter(out.readline, b''):
                q.put(l)
                if self._get_url(l) is not None:
                    break

        queue = Queue()
        thread = Thread(target=enqueue_output, args=(self._tb_proc.stderr, queue))
        thread.daemon = True
        thread.start()

        log = ""
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            time_remaining = timeout - (time.monotonic() - start_time)
            try:
                line = queue.get(timeout=time_remaining)
                url = self._get_url(line)
                if url is not None:
                    return url
                else:
                    log += line
            except Empty:
                continue

        raise Exception("Tensorboard did not report a listening URL. Log from Tensorboard follows:\n{}".format(log))

    def stop(self):
        """
        Stop this Tensorboard instance.

        :return: None
        """
        if self._tb_proc is None:
            module_logger.debug("Stop called but there's no TB process")
            return

        # Set the stop event before we do anything that needs us to wait
        self._event.set()
        self._event = None
        self._tb_proc.kill()
        self._job_handle = None
        self._tb_proc.wait()
        self._tb_proc = None
        self._executor.shutdown(wait=True)
        self._executor = None
        self._session.close()
        self._session = None

    def __del__(self):
        """
        Tensorboard destructor called during garbage collection to stop the tensorboard instance.

        :return: None
        """
        if self._tb_proc:
            self.stop()
