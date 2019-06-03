# -*- coding: utf-8 -*-

###
# Nathaniel Watson
# nathanielwatson@stanfordhealthcare.org
# 2019-05-16
###

import json
import jsonschema
import logging
from multiprocessing import Process, Queue, Lock
import os
import queue
import signal
import sys
import tarfile
import time

from google.cloud import storage, firestore

import psutil

import sruns_monitor as srm
import sruns_monitor.utils as utils
from sruns_monitor.sqlite_utils import Db

class ConfigException(Exception):
    pass

class MissingTarfile(Exception):
    pass

class Monitor:
    """
    Requires a configuration file in JSON format with settings regarding what folder to monitor
    and which GCP bucket to upload tarred runs to.
    """

    #: The presence of any file in this array indicates that the Run directory is ready for
    #: downstream processing (i.e. the Illumina NovaSeq has finished writing to the folder).
    #: The sential file can vary by sequencing platform. For NovaSeq, can use CopyComplete.txt.
    SENTINAL_FILES = set(["CopyComplete.txt"])

    def __init__(self, conf_file, verbose=False):
        #: If True, then verbose logging is enabled.
        self.verbose = verbose
        self.conf = self._validate_conf(conf_file)
        #: The name of the Firestore collection to use. 
        self.firestore_collection = self.conf["firestore_collection"]
        #: The Firestore connection to be used by the main thread only. 
        self.firestore = firestore.Client().collection(self.firestore_collection)
        self.watchdir = self.conf[srm.C_WATCHDIR]
        if not os.path.exists(self.watchdir):
            raise ConfigException("'watchdir' is a required property and the referenced directory must exist.".format(self.watchdir))
        self.completed_runs_dir = self.conf.get(srm.C_COMPLETED_RUNS_DIR)
        if not self.completed_runs_dir:
            self.completed_runs_dir = os.path.join(os.path.dirname(self.watchdir), "SRM_COMPLETED")
        if not os.path.exists(self.completed_runs_dir):
            os.mkdir(self.completed_runs_dir)
        #: The number of seconds to wait between run directory scans, with a default of 60.
        self.cycle_pause_sec = self.conf.get(srm.C_CYCLE_PAUSE_SEC, 60)
        #: The number of seconds that a child process running the workflow is allowed to run, after
        #: which the process will be killed. A value of 0 indicates that such a time limit will not
        #: be observed.
        self.process_runtime_limit_sec = self.conf.get(srm.C_TASK_RUNTIME_LIMIT_SEC, None)
        #: A `multiprocessing.Queue` instance that a child process will write to in the event that
        #: an Exception is to occur within that process prior to re-raising the Exception and exiting.
        #: The main process will check this queue in each scan iteration to report any child processes
        #: that have failed by means of logging and email notification.
        self.state = Queue() # Must pass in manually to multiprocessing.Process constructors.
        #: A lock for safeguarding access to logging streams.
        self.lock = Lock() # Must pass in manually to multiprocessing.Process constructors
        #: The GCP Storage bucket name in which tarred run directories will be stored.
        self.bucket_name = self.conf[srm.C_GCP_BUCKET_NAME]
        #: The directory in the bucket in which to store tarred run directories. If not provided,
        #: defaults to the root level directory.
        self.bucket_basedir = self.conf.get(srm.C_GCP_BUCKET_BASEDIR, "/")
        #signal.signal(signal.SIGTERM, self._cleanup)
        signal.signal(signal.SIGINT, self._cleanup)
        signal.signal(signal.SIGTERM, self._cleanup)
        #: The local sqlite database in which to store workflow status for a given run. If not provided,
        #: defaults to 'sruns.db'. See `sruns_monitor.sqlite_utils.Db` for more details on the
        #: structure of records in this database.
        self.db = Db(dbname=self.conf.get(srm.C_SQLITE_DB, "sruns.db"), verbose=self.verbose)

        self.logger = logging.getLogger(__name__)
        # Add debug file handler to self.logger:
        srm.add_file_handler(logger=self.logger, level=logging.DEBUG, tag="debug")
        # Add error file handler to self.logger:
        srm.add_file_handler(logger=self.logger, level=logging.ERROR, tag="error")

    def _validate_conf(self, conf_file):
        """
        Args:
            conf_file: `str`. The JSON configuration file.
        """
        conf_fh = open(conf_file)
        jconf = json.load(conf_fh)
        conf_fh.close()
        schema_fh = open(srm.CONF_SCHEMA)
        jschema = json.load(schema_fh)
        schema_fh.close()
        jsonschema.validate(jconf, jschema)
        return jconf

    def _validate_bucket(self):
        """
        Tries to create a `google.cloud.storage.bucket.Bucket` instance to ensure that we can
        connect to the bucket designated by `self.bucket_name`. If we can here, then a child process 
        should also be able to when it needs to. While we could store the bucket instance in our own 
        instance variable, it's probably not safe to share these amongst child processes, so better 
        to let each child process make it's own bucket instance. 
        """
        storage_client = storage.Client()
        # A `google.cloud.storage.bucket.Bucket` instance.
        self.client.get_bucket(self.bucket_name)

    def _cleanup(self, signum, frame):
        """
        Terminate all child processes. Normally this is called when a SIGTERM is caught

        Args:
            signum: Don't call explicitly. Only used internally when this method is serving as a
                handler for a specific type of signal in the funtion `signal.signal`.
            frame: Don't call explicitly. Only used internally when this method is serving as a
                handler for a specific type of signal in the funtion `signal.signal`.
        """
        signame = signal.Signals(signum).name
        self.logger.error("Caught signal {}. Preparing for shutdown.".format(signame))
        # email notification
        pid = os.getpid()
        child_processes = psutil.Process().children()
        # Kill child processes by sending a SIGKILL.
        [c.kill() for c in child_processes] # equiv. to os.kill(pid, signal.SIGKILL) on UNIX.
        self.db.curs.close()
        self.db.conn.close()
        sys.exit(128 + signum)

    def get_rundir_path(self, run_name):
        return os.path.join(self.watchdir, run_name)

    def _workflow(self, state, lock, run_name):
        """
        Runs the workflow. Knows which stages to run, which is useful if the workflow needs to
        be rerun from a particular point.

        This method is meant to serve as the value of the `target` parameter in a call to
        `multiprocessing.Process`, and is not meant to be called directly by users of this library.

        Args:
            state: `multiprocessing.Queue` instance.
            run_name: `str`. The name of a sequencing run.
        """
        rec = self.db.get_run(run_name)
        if not rec[self.db.TASKS_TARFILE]:
            self.task_tar(state=state, run_name=run_name, lock=lock)
        if not rec[self.db.TASKS_GCP_TARFILE]:
            self.task_upload(state=state, run_name=run_name, lock=lock)

    def firestore_update_status(self, run_name, status):
        """
        Update the status of a Firestore record. This method creates its own connection to the 
        Firestore database since child processes can call this method; hence, it does not use
        `self.firestore_connection`.
        """
        firestore_coll = firestore.Client().collection(self.firestore_collection)
        firestore_payload = {
            srm.FIRESTORE_ATTR_WF_STATUS: status
        }
        firestore_coll.document(run_name).set(firestore_payload)

    def task_tar(self, state,  run_name, lock ):
        """
        Creates a gzip tarfile of the run directory and updates the Firestore record's status to
        indicate that this task is running. The tarfile will be created in the directory
        being watched (`self.watchdir`) and named the same as the `run_name` parameter, but with
        a .tar.gz suffix.

        Once tarring is complete, the local database record is updated such that the attribute
        `sqlite_utils.Db.TASKS_TARFILE` is set to the path of the tarfile. Note that this method
        also updates the local database record to set the pid field with the process ID its running
        in.

        Args:
            state: `multiprocessing.Queue` instance.
            run_name: `str`. The name of a sequencing run.
        """
        try:
            self.db.update_run(name=run_name, payload={self.db.TASKS_PID: os.getpid()})
            rundir_path = self.get_rundir_path(run_name)
            tarball_name = rundir_path + ".tar.gz"
            with lock:
                self.logger.debug("Tarring sequencing run {}.".format(run_name))
            # Update status of Firestore record
            self.firestore_update_status(run_name=run_name, status=self.db.RUN_STATUS_TARRING)
            tarball = utils.tar(rundir_path, tarball_name)
            self.db.update_run(name=run_name, payload={self.db.TASKS_TARFILE: tarball_name})
            # Update status of Firestore record
            self.firestore_update_status(run_name=run_name, status=self.db.RUN_STATUS_TARRING_COMPLETE)
        except Exception as e:
            state.put((os.getpid(), e))
            # Let child process terminate as it would have so this error is spit out into
            # any potential downstream loggers as well. This does not effect the main thread.
            raise

    def task_upload(self, state, run_name, lock):
        """
        Uploads the tarred run dirctory to GCP Storage in the directory specified by `self.bucket_basedir`.
        The Firestore record's status is also updated to indicate that this task is running.
        The blob is named as $basedir/run_name/tarfile, where run_name is the squencing run name,
        and tarfile is the name of the tarfile produced by `self.task_tar`.

        Once uploading is complete, the local database record is updated such that the attribute
        `sqlite_utils.Db.TASKS_GCP_TARFILE` is set to the location of the blob as a string value
        formatted as '$bucket_name/blob_path'.
        Note that this method also updates the local database record to set the pid field with
        the process ID its running in.

        Finally, the local tarfile is removed.

        Args:
            state: `multiprocessing.Queue` instance.
            run_name: `str`. The name of a sequencing run.

        Raises:
            `MissingTarfile`: There isn't a tarfile for this run (based on the record information
            in self.db.
        """
        try:
            self.db.update_run(name=run_name, payload={self.db.TASKS_PID: os.getpid()})
            rec = self.db.get_run(run_name)
            tarfile = rec[self.db.TASKS_TARFILE]
            if not tarfile:
                raise MissingTarfile("Run {} does not have a tarfile.".format(run_name))
            # Upload tarfile to GCP bucket
            blob_name = self.create_blob_name(run_name=run_name, filename=tarfile)
            storage_client = storage.Client()
            # A `google.cloud.storage.bucket.Bucket` instance.
            bucket = storage_client.get_bucket(self.bucket_name)
            with lock:
                self.logger.debug("Uploading {} to GCP Storage bucket {} as {}.".format(tarfile,bucket, blob_name))
            # Update status of Firestore record
            self.firestore_update_status(run_name=run_name, status=self.db.RUN_STATUS_UPLOADING)
            utils.upload_to_gcp(bucket=bucket, blob_name=blob_name, source_file=tarfile)
            self.db.update_run(
                name=run_name,
                payload={self.db.TASKS_GCP_TARFILE: "/".join([self.bucket_name, blob_name])})
            # Remove local tarfile
            os.remove(tarfile)
            # Update status of Firestore record
            self.firestore_update_status(run_name=run_name, status=self.db.RUN_STATUS_UPLOADING_COMPLETE)
        except Exception as e:
            state.put((os.getpid(), e))
            # Let child process terminate as it would have so this error is spit out into
            # any potential downstream loggers as well. This does not effect the main thread.
            raise

    def create_blob_name(self, run_name, filename):
        """
        Creates a name for a blob object to be in GCP. The name is formulated as follows:

            self.bucket_basedir + '/' + run_name + '/' + os.path.basename(filename)

        There will not be a '/' at the start.
        """
        return "/".join([self.bucket_basedir, run_name, os.path.basename(filename)]).lstrip("/")

    def kill_childprocess_if_running_to_long(self, pid):
        """
        Args:
            pid: `int`. The process ID of a child process. 

        Returns:
            `Boolean`. `True` if the process was killed (kill signal sent) False otherwise. 
        """
        process = utils.get_process(pid)
        if process:
            if utils.running_too_long(process, self.process_runtime_limit_sec):
                process.kill()
                # The next iteration of the monitor will see that the pid isn't running and restart
                # the workflow if it hasn't finished yet. 

    def archive_run(self, run_name):
        """
        Moves the run directory to the completed runs directory.
        """
        from_path = self.get_rundir_path(run_name)
        to_path = os.path.join(self.completed_runs_dir, run_name)
        self.logger.debug("Moving run {run} to completed runs location {loc}.".format(run=run_name, loc=to_path))
        os.rename(from_path, to_path)

    def process_new_run(self, run_name):
        """
        Create a new record into the local sqlite db as well as the Firestore db.
        """
        self.db.insert_run(name=run_name)
        # Create Firestore document
        firestore_payload = {
            srm.FIRESTORE_ATTR_WF_STATUS: self.db.RUN_STATUS_STARTING
        }
        self.firestore.document(run_name).set(firestore_payload)
        self.run_workflow(run_name)

    def process_completed_run(self, run_name, archive=True):
        """
        Moves the run directory to the completed runs directory location that is defined
        by `sruns_monitor.C_COMPLETED_RUNS_DIR`.

        Updates Firestore to set

            * the GCP storage attribute (identified by the variable `sruns_monitor.FIRESTORE_ATTR_STORAGE`)
              to the location of the gzip tarfile of the run directory in GCP bucket storage. This
              value is extracted from the local record in the SQLite database, and is formatted as
              '$bucket_name/blob_path'.
            * the workflow status attribute (identified by the variable `sruns_monitor.FIRESTORE_ATTR_WF_STATUS`.
              to completed.

        Args:
            run_name: `str`.
            archive: `boolean`. True meas to move the run directory to the completed runs location.

        """
        rec = self.db.get_run(run_name)
        if archive:
            self.archive_run(run_name)
        # Update Firestore record
        firestore_payload = {
            srm.FIRESTORE_ATTR_WF_STATUS: self.db.RUN_STATUS_COMPLETE,
            srm.FIRESTORE_ATTR_STORAGE: rec[self.db.TASKS_GCP_TARFILE]
        }
        self.firestore.document(run_name).update(firestore_payload)

    def run_workflow(self, run_name):
        p = Process(target=self._workflow, args=(self.state, self.lock, run_name))
        p.start()

    def scan(self):
        """
        Finds all sequencing run in `self.watchdir` that are finished sequencing.
        """
        run_names = []
        for run_name in os.listdir(self.watchdir):
            rundir_path = self.get_rundir_path(run_name)
            if not os.path.isdir(rundir_path):
                continue
            if set(os.listdir(rundir_path)).intersection(self.SENTINAL_FILES):
                # This is a completed run directory
                run_names.append(run_name)
        return run_names

    def process_rundirs(self, run_names):
        """
        For each sequencing run name, checks it's status with regard to the workflow and initiates
        any remaining steps, i.e. restart, cleanup, ...
        """
        for run_name in run_names:
            self.logger.debug("Processing rundir {}".format(run_name))
            run_status = self.db.get_run_status(run_name)
            if run_status == self.db.RUN_STATUS_NEW:
                self.process_new_run(run_name)
            elif run_status == self.db.RUN_STATUS_COMPLETE:
                self.process_completed_run(run_name)
            elif run_status == self.db.RUN_STATUS_RUNNING:
                # Check if it has been running for too long.
                rec = self.db.get_run(run_name)
                pid = rec[self.db.TASK_PID]
                if self.kill_childprocess_if_running_to_long(pid):
                    # Send email notification 
                    pass
            elif run_status == self.db.RUN_STATUS_NOT_RUNNING:
                self.run_workflow(run_name)

    def start(self):
        cycle_num = 0
        try:
            while True:
                cycle_num += 1
                print("Cycle", cycle_num)
                # Remove any zombie processes
                # Curious why or how this works? See book Programming Python, 4th ed. section
                # "Killing the zombies: Don't fear the reaper!".
                try:
                    os.waitpid(0, os.WNOHANG)
                    # The 0 argument above means to check for any child process, not one with a
                    # specific pid.
                except ChildProcessError:
                    pass # No child processes
                finished_rundirs = self.scan()
                self.process_rundirs(run_names=finished_rundirs)
                # Now check the shared queue object to see if any child process ran into some trouble
                # and recorded its dying last words:
                child_process_msg = None
                try:
                    child_process_msg = self.state.get(block=False)
                except queue.Empty:
                    pass
                if child_process_msg:
                    pid = child_process_msg[0]
                    msg = child_process_msg[1]
                    self.logger.error("Process {} exited with message '{}'.".format(pid, msg))
                    # Email notification
                time.sleep(self.cycle_pause_sec)
        except Exception as e:
            # Email notification
            self.logger.error("Main process Exception: {}".format(e))
            raise

### Example
# m = Monitor(conf_file="my_conf_file.json")
# m.start()
###
