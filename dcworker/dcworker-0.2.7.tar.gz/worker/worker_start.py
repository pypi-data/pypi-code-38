import copy
import os.path
from multiprocessing import Process
from os import listdir
from os.path import exists, join, dirname, isfile, \
    isdir, getsize
from sys import platform
from time import sleep
from typing import Dict, Any, List

import docker
import dcdataset
from dcdataset.utils import extract_compressed_file

from common.dbinterface import *
from common.global_variable import *
from common.training_task import TrainingTask
from common.util.common_utils import *
from worker.worker_log.user_logger import UserLogStream
from worker.worker_log.worker_logger import worker_logger
from worker.worker_runtime import *

###############################################################################

WORKER_RUN_ENV_TASK_UUID = "TASK_UUID"
WORKER_RUN_ENV_TASK_INDEX = "TASK_INDEX"
WORKER_RUN_ENV_TASK_CLUSTER_SPEC = "CLUSTER_SPEC"
WORKER_RUN_ENV_TASK_ROLE = "TASK_ROLE"
WORKER_RUN_ENV_WORKER_TYPE = "WORKER_TYPE"
WORKER_RUN_ENV_WORKER_RESOURCE_ID = "RESOURCE_ID"
WORKER_RUN_ENV_DATASET_DIR = "DATASET"
WORKER_RUN_ENV_CODE_DIR = "CODE"
WORKER_RUN_ENV_OUTPUT_DIR = "OUTPUT"
WORKER_RUN_ENV_LOG_DIR = "LOG"
WORKER_RUN_ENV_COMMAND = "COMMAND"

CONTAINER_WORK_DIR = "/runtime"
CONTAINER_DATASET_DIR_LOCATION = "/data"
CONTAINER_CODE_DIR_LOCATION = "{}/{}".format(CONTAINER_WORK_DIR, CODE_DIR_NAME)
CONTAINER_OUTPUT_DIR_LOCATION = "{}/{}".format(CONTAINER_WORK_DIR, OUTPUT_DIR_NAME)
CONTAINER_LOG_DIR_LOCATION = "{}/{}".format(CONTAINER_WORK_DIR, LOG_DIR_NAME)

PROVISIONED_WORKER_WORKER_RUN_PATH = "{}/{}".format(CONTAINER_WORK_DIR, "worker_run.py")

###############################################################################

os_platform = None
if platform.startswith("linux"):
    os_platform = LINUX
elif platform.startswith("win"):
    os_platform = WIN
else:
    raise Exception("{} is not supported".format(str(platform)))


###############################################################################

class TaskContext(object):
    exec_process = None
    log_process = None
    retry_count = 10
    logdir = None
    container_alive_states = ["running", "created"]
    user_log_stream = None
    is_alive = True

    def __init__(self, logger, logdir, exec_process=None, exec_container=None):
        self.exec_process = exec_process
        self.exec_container = exec_container
        self.logger = logger
        self.logdir = logdir
        # Sanity check: exactly one of exec_process and exec_container must be
        # present.
        if exec_process is not None and exec_container is not None:
            raise RuntimeError("cannot run in both bare metal and container mode")
        elif exec_process is None and exec_container is None:
            raise RuntimeError("no running context")

    def monitor(self):
        if self.exec_process is not None:
            alive = True if self.exec_process.poll() is None else False
        else:
            self.exec_container.reload()
            self.logger.log_info(
                "TaskContext",
                "container state: {}".format(self.exec_container.status))

            alive = True if self.exec_container.status in self.container_alive_states else False

        # If there is a failure marker, this run is not graceful (i.e. our
        # code failed).
        graceful = True
        failure_path = join(self.logdir, WORKER_FAILED_MARKER)
        if exists(failure_path):
            graceful = False
            with open(failure_path, "r") as f:
                self.logger.log_error(
                    "TaskContext",
                    "monitor error: {}".format(f.read()))

        self.is_alive = alive
        return alive, graceful

    def terminate(self):
        if self.exec_process is not None and self.exec_process.poll() is None:
            self.exec_process.kill()
        elif self.exec_container is not None:
            self.exec_container.reload()
            if self.exec_container.status in self.container_alive_states:
                try:
                    self.exec_container.kill()
                except:
                    pass

        if self.log_process.is_alive():
            self.log_process.terminate()
            self.log_process.join()

        return

    def can_retry(self):
        if self.retry_count <= 0:
            return False

        self.retry_count -= 1
        return True

    def dump_output(self):
        if self.exec_process is not None:
            self.exec_process.wait()
            while self.exec_process.poll() is None:
                line = self.exec_process.stdout.readline().decode('utf-8')
                if line and line != "":
                    self.logger.log_info("exec_process", line.rstrip('\n'))
        else:
            self.exec_container.wait()
            output = self.exec_container.logs().decode().split('\n')
            for line in output:
                self.logger.log_info("exec_container", line.rstrip('\n'))


###############################################################################

class Worker(object):
    # local ip and port
    auth_token = None
    worker_type = None
    resource_id = None
    last_error = None
    worker_logger = None
    temp_token = None
    tensorboard_process = None
    task = None
    task_uuid = None
    task_context = None

    def __init__(self,
                 master_server,
                 port,
                 workdir,
                 toplevel_datadir,
                 worker_uuid,
                 worker_machine_type,
                 gpu_id=-1,
                 worker_info="",
                 worker_type="gpu",
                 passcode=None):

        # local endpoint http://127.0.0.1:8000
        self.master_endpoint = master_server
        self.port = port
        self.workdir = workdir
        self.toplevel_datadir = toplevel_datadir
        self.worker_logger = worker_logger(worker_uuid)
        self.resource_id = gpu_id
        self.worker_info = worker_info
        self.worker_uuid = worker_uuid
        self.worker_type = worker_type
        self.passcode = passcode
        self.worker_machine_type = worker_machine_type

    # --------------------------------------------------------------------------

    # register worker to create account
    # return {success}, {uuid}
    @classmethod
    def register(cls, master_endpoint, task_uuid=None):
        register_logger = worker_logger(os.getpid())
        request_body = {}
        if task_uuid is not None:
            request_body["task_uuid"] = task_uuid

        success, status_code, response_body, error_message = request_server(
            master_endpoint + "/api/v1/worker/register/",
            'post',
            **{"data": request_body})

        if not success:
            register_logger.log_error("register", error_message)
            return False, None, None

        if status_code == 200:
            uuid = response_body.get("uuid", None)
            if not uuid:
                register_logger.log_error("register", "unexpected uuid from server")
                return False, None, None

            register_logger.log_info("register", "worker uuid: {0}".format(uuid))
            passcode = response_body.get("passcode", None)
            if not uuid:
                register_logger.log_error("register", "unexpected passcode from server")
                return False, None, None

            register_logger.worker_id = uuid
            register_logger.log_info("register", "worker register succeed")
            return True, uuid, passcode
        else:
            register_logger.log_error("register", "status {0}, error '{1}'".format(
                status_code,
                response_body.get("error")))

            return False, None, None

    # --------------------------------------------------------------------------

    '''

        @abstract

            Expect:
                self.master_endpoint: <str>
                self.worker_uuid: <str>
                self.worker_type: <str> ("cpu" | "gpu")
                self.resource_id: <int>
                self.passcode: <str>
                self.workdir: <str>

            Produce:
                All files inside self.workdir will be deleted.
                self.auth_token: <TokenAuth> will contain the token for
                interacting with the master server.
                self.task set to None.
                self.task_uuid set to None.

        @returns
            success
            - success: <bool> Whether the enroll was successful.

    '''

    def enroll(self, fake_enroll_response: Dict[str, Any] = None):
        self.task_uuid = None
        self.task = None
        if self.worker_uuid is None:
            self.worker_logger.log_error("enroll", "missing worker uuid")
            return False

        # Get uuid of the worker, update the logger.
        self.worker_logger.worker_id = self.worker_uuid

        # Validate workdir
        if self.workdir is None:
            self.worker_logger.log_error("enroll", "None workdir")
            return False

        if not isdir(self.workdir):
            self.worker_logger.log_warning(
                "enroll",
                "invalid workdir: {}. Attempt to make a new one".format(
                    self.workdir))

            try:
                os.mkdir(self.workdir)
            except Exception as e:
                self.worker_logger.log_error(
                    "enroll",
                    "failed to create workdir at {}, error: {}".format(
                        self.workdir,
                        str(e)))

                traceback.print_exc()
                return False

        # Clear the workdir.
        self._cleanup_workdir()

        # Get type of the worker, update the logger.
        if self.worker_type != "cpu" and self.worker_type != "gpu":
            self.worker_logger.log_error(
                "enroll",
                "unexpected type for the worker: {}".format(self.worker_type))

            return False

        self.worker_logger.worker_type = self.worker_type
        self.worker_logger.resource_id = self.resource_id

        # Get passcode of the worker.
        if self.passcode is None:
            self.worker_logger.log_error(
                "enroll",
                "cannot find passcode for the worker")

            return False

        # First attempt to see if there is a simulated enroll. If not, request
        # the server for real enroll.
        request_body = {
            'uuid': self.worker_uuid,
            'passcode': self.passcode,
            'worker_info': self.worker_info}

        success, \
        status_code, \
        response_body, \
        error_message = request_server(
            self.master_endpoint + "/api/v1/worker/enroll/",
            'post',
            **{"data": request_body})

        # if there is fake_enroll_response
        # update corresponding values in the actual response
        if fake_enroll_response is not None:
            response_body.update(fake_enroll_response)
            status_code = 200
            success = True

        if not success:
            self.worker_logger.log_error("enroll", error_message)
            return False

        if status_code == 200:
            auth_token = response_body.get('auth_token', None)
            if not auth_token:
                self.worker_logger.log_error(
                    "enroll",
                    "no auth token from server")

                return False

            self.auth_token = TokenAuth(auth_token)
            self.worker_logger.log_info("enroll", "success")
            return True
        else:
            self.worker_logger.log_error("enroll",
                                         "status code {0}, error {1}".format(
                                             status_code,
                                             response_body.get("error")))

            return False

    # --------------------------------------------------------------------------

    '''

        @abstract

            Expect:
                self.auth_token: <TokenAuth>
                self.master_endpoint: <str>

            Produce:
                self.task_uuid: <str> will contain the uuid of the task.
                self.task: <TrainTask> will contain the task information.
                self.temp_token: <dict> will contain the S3 authentication for
                fetching code and data.

        @returns
            success, task_ready, re_enroll, need_cleanup
            - success: <bool> Whether API is successful.
            - task_ready: <bool> Whether polled a task.
            - re_enroll: <bool> Whether need to re-enroll.
            - need_cleanup: <bool> Whether task_cleanup must be called.

    '''

    def poll(self, is_poll_no_task: bool = False, simulate_job_response: Dict[str, Any] = None):
        self.task = None
        self.task_uuid = None
        if self.auth_token is None:
            self.worker_logger.log_error(
                "poll",
                "worker has no auth token, need enroll")

            return False, False, True, False

        if is_poll_no_task:
            self.worker_logger.log_info(
                "poll",
                "no task is ready for the worker [simulated]")

            return True, False, False, False

        request_body = {'port': self.port}

        success, \
        status_code, \
        response_body, \
        error_message = request_server(
            self.master_endpoint + "/api/v1/worker/poll/",
            'post',
            **{"data": request_body,
               "auth": self.auth_token})

        # if there is simulated job response
        # update corresponding values in the actual response
        if simulate_job_response is not None:
            response_body.update(simulate_job_response)

            # Set status code to 200.
            success = True
            status_code = 200

        if not success:
            self.worker_logger.log_error("poll", error_message)
            # Requesting server failed. Since we are in poll, there must
            # not be a task associated with the worker. Exit.
            # Note: in this case, there is no need to call task_cleanup
            # as there is no real task polled.
            return False, False, False, False

        # Server indicates that no task is ready for the worker.
        if status_code == 202:
            return True, False, False, False

        # Server indicates that a task is ready for the worker.
        elif status_code == 200:
            self.worker_logger.log_info("poll", "task is ready for the worker")

            try:
                # config is a required key in response body,
                # raise exception if it does not exist
                config =  json.loads(response_body["config"])
                task = TrainingTask(**config)
            except Exception as e:
                self.worker_logger.log_error(
                    "poll",
                    "unexpected task config from server: {}".format(str(e)))

                # Note that here we need to clean up the task as we've
                # already polled it.
                return False, False, False, True

            self.task = task
            self.task_uuid = self.task.task_uuid
            return True, True, False, False

        # Server indicates that the current auth_token is no longer valid.
        elif status_code == 401:
            self.worker_logger.log_error(
                "poll",
                "auth_token expired. worker needs to enroll again")

            return False, False, True, False

        # Other errors from server.
        else:
            self.worker_logger.log_error(
                "poll",
                "status code {}, error {}".format(
                    status_code,
                    response_body.get("error")))

            return False, False, False, False

    # --------------------------------------------------------------------------

    '''

        @abstract

            Wait for a while before attempt polling again.

        @returns
            None. This routine always succeeds.

    '''

    def poll_wait(self):
        sleep(30)

    # --------------------------------------------------------------------------

    '''

        @abstract

            Expect:
                self.task_uuid: <str>
                self.temp_token: <dict>
                self.task: <TrainingTask>
                self.toplevel_datadir: <str>

            Produce:
                code is downloaded to /workdir/CODE_DIR_NAME/
                dataset is downloaded to /toplevel_datadir/dataset_name/
                self.task.dataset_name: <str> will contain the name of the
                dataset referenced.
                self.task.dataset_local_path: <str> will contain the local path
                to the dataset.

        @returns
            success
            - success: <bool> Whether successfully downloaded everything.

    '''

    def fetch(self,
              download_code: bool = True,
              download_dataset: bool = True):

        # Download code to /workdir/CODE_DIR_NAME/
        try:
            if download_code:
                success = self._download_code()
                if not success:
                    return False
        except Exception as e:
            self.worker_logger.log_error(
                "fetch",
                "failed to fetch code: {}".format(str(e)))

            traceback.print_exc()
            return False

        # download dataset
        try:
            if download_dataset:
                success = self._download_dataset()
                if not success:
                    return False
        except Exception as e:
            self.worker_logger.log_error(
                "fetch",
                "failed to fetch dataset: {}".format(str(e)))

            traceback.print_exc()
            return False

        return True

    def _download_unzip_in_dir(self, dir):
        # This routine unzip the TAR.GZ files inside the given dir. And it will
        # delete all the zip files.
        for item in os.listdir(dir):
            path = join(dir, item)
            if isfile(path):
                if item.lower().endswith(EXTENSION_TAR_GZ):
                    # TODO: This routine does not handle nested zip files.
                    # Should it? Also, it does not check whether the files
                    # unzipped will be a collision with the existing files.
                    unzip_tarfile(path, dir)
                    os.remove(path)

    def _download_from_presigned_url(self, download_to, download_urls):
        try:
            for (hint, url) in download_urls:
                response = requests.get(url, allow_redirects=True)
                if not response.ok:
                    self.worker_logger.log_error(
                        "download",
                        "cannot download dataset from {}".format(url))

                    return False

                file_loc = join(download_to, hint)
                with open(file_loc, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size=128):
                        fd.write(chunk)

                # Sanity check the file is written.
                if not isfile(file_loc):
                    self.worker_logger.log_error(
                        "download",
                        "cannot find downloaded code at {}".format(file_loc))

                    return False

                self.worker_logger.log_info(
                    "download",
                    "download code from {} to {}".format(
                        url,
                        file_loc))

            return True
        except Exception as e:
            self.worker_logger.log_error(
                "download",
                "cannot download dataset: {}".format(str(e)))
            traceback.print_exc()
            return False

    def _download_code(self):
        code_dir = self._get_code_dir_location()
        os.makedirs(code_dir)

        # Get code PreSigned URLs. Note that code must always be in the download
        # urls as validated already inside poll.
        code_download_urls = self.task.download_info[JOB_CONTENT_TYPE_CODE]
        success = self._download_from_presigned_url(code_dir, code_download_urls)
        if not success:
            return False

        # Finally unzip the code downloaded.
        self._download_unzip_in_dir(code_dir)
        return True

    def _download_dataset(self):
        # Only worker needs to download datasets.
        if self.task.task_role != "worker":
            return True

        # Note that for worker role, dataset must be in the download urls as
        # validated by poll.
        download_info = self.task.download_info
        self.worker_logger.log_info(
            "download_dataset",
            "Download info is {}".format(json.dumps(download_info)))

        '''
        download_info should be
            code: code presign url
            dataset: {
                'url': presigned url,
                'dataset_name': dataset_name, which is job_uuid
            known_datasets: [
                'cifar10'
            ]
        '''
        if JOB_CONTENT_TYPE_KNOWN_DATASETS in download_info:
            # download known_dataset and increment their reference
            success = self._download_known_dataset(
                            download_info[JOB_CONTENT_TYPE_KNOWN_DATASETS])

            if not success:
                return False

        if JOB_CONTENT_TYPE_CUSTOM_DATASET in download_info:
            success = self._download_custom_dataset(
                            download_info[JOB_CONTENT_TYPE_CUSTOM_DATASET])

            if not success:
                return False

        return True

    def _unreference_dataset(self):
        """
        decrement all used dataset reference. remove dataset record if has no more reference and is not known dataset
        Returns:

        """

        if self.worker_machine_type != WORKER_MACHINE_DEEPCLUSTER_STANDARD:
            return

        # Only worker needs to use datasets.
        if self.task.task_role != "worker":
            return

        dataset_names = []
        custom_dataset_dict = self.task.download_info.get(JOB_CONTENT_TYPE_CUSTOM_DATASET, None)
        if custom_dataset_dict is not None:
            dataset_names.append(custom_dataset_dict['dataset_name'])

        known_datasets = self.task.download_info.get(JOB_CONTENT_TYPE_KNOWN_DATASETS, None)
        if known_datasets is not None and isinstance(known_datasets, list):
            dataset_names += known_datasets

        for dataset_name in dataset_names:
            success, delete_local = delete_dataset_sync(dataset_name)
            if not success:
                self.worker_logger.log_error(
                    "unreference_dataset",
                    "db error for unreference the dataset: {}!".format(dataset_name))

            elif delete_local:
                # remove directory ignore error if dir does not exists
                shutil.rmtree(self.task.dataset_local_path, ignore_errors=True)

    def _download_known_dataset(self, known_datasets: List[str]) -> bool:
        """
            known_datasets: [
                'cifar10'
            ]
        :return:
        """
        if not isinstance(known_datasets, list):
            self.worker_logger.log_error("_download_known_dataset",
                                         "known_datasets is not a dictionary but {}".format(
                                             type(known_datasets)),
                                         task_id=self.task_uuid)
            return False

        for dataset_name in known_datasets:
            is_existed = self._wait_and_increment_dataset_reference(
                            dataset_name,
                            is_dataset_persisted=1)

            dataset_local_path = self._get_dataset_local_path(dataset_name)

            # store in the training task for mounting into container
            self.task.known_datasets[dataset_name] = dataset_local_path

            # download dataset if not exists else skip download
            success = dcdataset.download_dataset_by_name(
                        dataset_name=dataset_name,
                        destination_dir=dataset_local_path)

            if not success:
                self.worker_logger.log_error("_download_known_dataset",
                                             "failed to download dataset: {}".format(dataset_name),
                                             task_id=self.task_uuid)
                delete_dataset_sync(dataset_name)
                shutil.rmtree(dataset_local_path, ignore_errors=True)

                return False
            elif not is_existed:
                # first time download dataset, mark ready
                if self.worker_machine_type == WORKER_MACHINE_DEEPCLUSTER_STANDARD:
                    execute_query_on_table(DATASET_SET_READY_COMMAND, (dataset_name,))

        return True

    def _download_custom_dataset(self, custom_dataset_info: Dict[str, str]) -> bool:
        """
            download custom dataset from presigned url to local
            directory name is the dataset_name assigned by master server
            dataset: {
                'url': presigned url,
                'dataset_name': dataset_name, which is job_uuid
        Returns:
            indicate if the dataset is ready
        """
        # TODO: this might not work for distributed training
        #  where two task for same job try to download at the same time

        # Download from dataset_download_urls into dataset_local_path.
        url = custom_dataset_info.get('url')
        dataset_name = custom_dataset_info.get('dataset_name')
        dataset_local_path = self._get_dataset_local_path(dataset_name)

        # this path is mount directly to user with env variable $DATASET
        self.task.dataset_local_path = dataset_local_path

        if not isdir(dataset_local_path):
            os.makedirs(dataset_local_path)
            is_existed = self._wait_and_increment_dataset_reference(
                            dataset_name,
                            is_dataset_persisted=0)

            success = self._download_from_presigned_url(
                dataset_local_path,
                url)
            if not success:
                self.worker_logger.log_error("_download_custom_dataset",
                                             "failed to download custom dataset from {}".format(url),
                                             task_id=self.task_uuid)
                shutil.rmtree(dataset_local_path, ignore_errors=True)

                return False

            # uncompress data.tar.gz
            for file in listdir(dataset_local_path):
                extract_compressed_file(join(dataset_local_path, file), True)

            if not is_existed:
                # first time download dataset, mark ready
                if self.worker_machine_type == WORKER_MACHINE_DEEPCLUSTER_STANDARD:
                    execute_query_on_table(DATASET_SET_READY_COMMAND, (dataset_name,))

        return True

    def _wait_and_increment_dataset_reference(self,
                                              dataset_name: str,
                                              is_dataset_persisted: int) -> bool:
        """
        always increment reference to the dataset when use
        wait when the dataset has ref count but not ready, else dataset increment and download if needed
        exists but not ready -> wait
        exits and ready -> return True
        not exits -> return False
        Args:
            dataset_name: dataset name which is the folder name of the dataset
            is_dataset_persisted: indicates if dataset is ready to use

        Returns:
            indicates if the dataset exists and ready
        """

        # If the machine is not deepcluster standard, just return False to
        # directly download dataset.
        if self.worker_machine_type != WORKER_MACHINE_DEEPCLUSTER_STANDARD:
            return False

        dataset_local_path = self._get_dataset_local_path(dataset_name)

        wait_count = 60
        output = None
        while wait_count > 0:
            sleep(10)
            success, output = query_from_table(DATASET_QUERY_BY_DATASET_NAME_COMMAND,
                                               params=(dataset_name,))
            if not success:
                self.worker_logger.log_error("_wait_and_increment_dataset_reference",
                                             "failed to query database for dataset {}".format(dataset_name))
                return False
            if len(output) > 0 and output[0][3] == 0:
                # someone has ref to this dataset but not yet finish downloading
                wait_count -= 1
                continue
            else:
                # either no one has ref to it or it is already finished download
                # proceed to increment refcount and download if not exists
                break

        # increment dataset refcount by name
        increment_dataset_reference(dataset_name, dataset_local_path, is_dataset_persisted, 0)

        # indicates if the dataset exists and must be ready
        return len(output) > 0

    # --------------------------------------------------------------------------

    '''

        @abstract

            Expect:
                self.task_uuid: <str>
                self.task: <TrainingTask>

            Produce:
                user environment is installed to /workdir/VENV/
                output folder is created at /workdir/OUTPUT_DIR_NAME/
                log folder is created at /workdir/LOG_DIR_NAME/

        @returns
            success
            - success: <bool> Whether successfully prepared for run.

    '''

    def pre_run(self):
        # Make a output_dir
        os.mkdir(self._get_output_dir_location())
        # Make a log_dir
        os.mkdir(self._get_log_dir_location())

        # Note that even if there is not requirements.txt, a VENV will be created.
        requirements_file = join(self._get_code_dir_location(),
                                 REQUIREMENTS_TXT)

        if exists(requirements_file):
            self.worker_logger.log_info(
                "pre_run",
                "requirements_file at {} with size = {} bytes".format(
                    requirements_file,
                    getsize(requirements_file)))
        else:
            self.worker_logger.log_info(
                "pre_run",
                "requirements_file does not exist".format(
                    requirements_file))

        self.worker_logger.log_info(
                "pre_run",
                "worker machine type: {}".format(self.worker_machine_type))

        success = True
        if self.worker_machine_type == WORKER_MACHINE_PROVISIONED:
            # If the worker machine is a provisioned machine from other provider,
            # then currently we must already run in an container. Just install
            # the user requirement.
            success = self._install_user_requirements_for_provisioned_worker(requirements_file)
        elif self.worker_machine_type == WORKER_MACHINE_DEEPCLUSTER_STANDARD:
            # If the worker machine is deepcluster standard machine, pull the
            # container image.
            success = self._pull_container_image()
        else:
            self.worker_logger.log_info(
                "pre_run",
                "worker machine type `{}` is not supported".format(
                    self.worker_machine_type))

            success = False

        return success

    def _install_user_requirements_for_provisioned_worker(self, requirements_file):
        if not exists(requirements_file) or getsize(requirements_file_host) == 0:
            self.worker_logger.log_info(
                "pre_run",
                "worker no need to install user requirements")

            return True


        # We must be currently running in containers. Conda environment
        # must have been activated.  Thus, directly invoke conda for install
        # the requirements.
        self.worker_logger.log_info(
                "pre_run",
                "worker install user requirements at {}".format(
                    requirements_file))

        p = subprocess.Popen(["conda",
                              "install",
                              "--file",
                              requirements_file],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        while p.poll() is None:
            line = p.stdout.readline().decode('utf-8')
            if line and line != "":
                self.worker_logger.log_info("pre_run::venv", line.rstrip('\n'))

        p.wait()
        return True

    def _pull_container_image(self):
        try:
            self.worker_logger.log_info(
                "pre_run",
                "pull container image: {}".format(self._get_container_image()))

            name = self._get_container_image_name()
            tag = self._get_container_image_tag()
            docker_client = docker.from_env()
            image = docker_client.images.pull(name, tag=tag)
            if not image:
                self.worker_logger.log_error(
                    "pre_run",
                    "cannot find image")

                return False

            return True
        except Exception as e:
            self.worker_logger.log_error(
                "pre_run",
                "pull container image: {}".format(str(e)))

            traceback.print_exc()
            return False

    # --------------------------------------------------------------------------

    '''

        @abstract

            Expect:
                self.task_uuid: <str>
                self.task: <TrainingTask>
                code is placed at <WORKER_CWD>/workdir/CODE_DIR_NAME/
                dataset is downloaded at self.task.dataset_local_path
                virtualenv is placed at <WORKER_CWD>/VENV/
                output folder is created at /workdir/OUTPUT_DIR_NAME/
                log folder is created at /workdir/LOG_DIR_NAME/

                When running in container:
                    - <WORKER_CWD> = '/runtime'
                    - dataset will be mounted at '/data'
                    - The file layout looks like:
                        /data  <= self.task.dataset_local_path folder mounted as '/data' [Read-Only]
                            user_data.json
                        /runtime
                            /venv <= 'workdir/VENV' folder mounted as '/runtime/venv' [Read-Write]
                                /bin
                                    Python
                                /lib
                                    <user_packages>
                            /code <= 'workdir/code' folder mounted as '/runtime/code' [Read-Write] <= CWD
                                user_code.py
                                main.py
                            worker_run.py
                        /output <= 'workdir/output' folder mounted as '/output' [Read-Write]
                            user_output.txt

                When running on bare metal:
                    - <WORDER_CWD> = self.workdir
                    - dataset will be placed at self.task.dataset_local_path
                    - The file layout looks like:
                        /self.task.dataset_local_path
                            user_data.json
                        /workdir
                            /venv
                                /bin
                                    Python
                                /lib
                                    <user_packages>
                            /code <= CWD
                                user_code.py
                                main.py
                            /output
                                user_output.txt

            Produce:
                self.task_context: <TaskContext> will contain the task context.

        @returns
            None - After passing pre_run stage, always go to post_run stage.

    '''

    def run(self, container_config: Dict[str, Any] = None):
        self.worker_logger.log_info(
            "run",
            "{} task: {}".format(self.task.task_role, self._get_current_task_uuid()))

        # Prepare environment variables.
        env = {
            WORKER_RUN_ENV_TASK_UUID: str(self._get_current_task_uuid()),
            WORKER_RUN_ENV_TASK_INDEX: str(self.task.task_index),
            WORKER_RUN_ENV_TASK_CLUSTER_SPEC: json.dumps(self.task.cluster_spec),
            WORKER_RUN_ENV_WORKER_TYPE: str(self.worker_type),
            WORKER_RUN_ENV_WORKER_RESOURCE_ID: str(self.resource_id),
            WORKER_RUN_ENV_TASK_ROLE: str(self.task.task_role)
        }

        if self.worker_machine_type == WORKER_MACHINE_PROVISIONED:
            # For provisioned machine, we are already running in container.
            # Just use the locations directly.
            env[WORKER_RUN_ENV_DATASET_DIR] = str(self.task.dataset_local_path)
            env[WORKER_RUN_ENV_CODE_DIR] = str(self._get_code_dir_location())
            env[WORKER_RUN_ENV_OUTPUT_DIR] = str(self._get_output_dir_location())
            env[WORKER_RUN_ENV_LOG_DIR] = str(self._get_log_dir_location())
            # Command to execute
            env[WORKER_RUN_ENV_COMMAND] = json.dumps(self.task.command)
            exec_process = self._execute_provisioned_worker(env)
            task_context = TaskContext(self.worker_logger,
                                       self._get_log_dir_location(),
                                       exec_process=exec_process)

        elif self.worker_machine_type == WORKER_MACHINE_DEEPCLUSTER_STANDARD:
            # For container run, dataset folder is mounted to
            # self._get_container_dataset_path.
            env[WORKER_RUN_ENV_DATASET_DIR] = str(self._get_container_dataset_path())
            # Code folder is self._get_container_code_dir_location
            env[WORKER_RUN_ENV_CODE_DIR] = str(self._get_container_code_dir_location())
            # Output folder is self._get_container_output_dir_location
            env[WORKER_RUN_ENV_OUTPUT_DIR] = str(self._get_container_output_dir_location())
            # Log folder is self._get_container_log_dir_location
            env[WORKER_RUN_ENV_LOG_DIR] = str(self._get_container_log_dir_location())
            # Command to execute
            env[WORKER_RUN_ENV_COMMAND] = json.dumps(self.task.command)
            exec_container = self._execute_container(env, container_config)
            task_context = TaskContext(self.worker_logger,
                                       self._get_log_dir_location(),
                                       exec_container=exec_container)

        else:
            # We should not hit here, as pre_run would have failed already.
            return

        self.task_context = task_context
        self._start_streaming_log()
        return

    def _start_streaming_log(self):
        self.task_context.user_log_stream = UserLogStream(self.task_context,
                                                          self._get_current_job_uuid(),
                                                          self._get_current_task_uuid(),
                                                          self.master_endpoint,
                                                          self.auth_token)

        log_file = self._get_user_log_file()
        log_process = Process(target=self.task_context.user_log_stream.stream_log,
                              args=("user", log_file))

        log_process.start()
        self.task_context.log_process = log_process

    def _execute_provisioned_worker(self, env):
        exec_process = subprocess.Popen(["python",
                                         self._get_provisioned_worker_worker_run_path()],
                                        cwd=self._get_code_dir_location(),
                                        env=env)

        return exec_process

    def _execute_container(self, env, container_config):
        requirements_file_host = join(self._get_code_dir_location(),
                                      REQUIREMENTS_TXT)

        requirements_file_container = join(self._get_container_code_dir_location(),
                                           REQUIREMENTS_TXT)

        # worker_run.py is directly under /runtime.
        worker_run_path = "{}/{}".format(CONTAINER_WORK_DIR, "worker_run.py")

        # Build a mount mapping.
        mount_command = {
            self._get_code_dir_location(): {'bind': self._get_container_code_dir_location(), 'mode': 'rw'},
            self._get_output_dir_location(): {'bind': self._get_container_output_dir_location(), 'mode': 'rw'},
            self._get_log_dir_location(): {'bind': self._get_container_log_dir_location(), 'mode': 'rw'},

        }

        if self.task.dataset_local_path is not None:
            mount_command[self.task.dataset_local_path] = {'bind': self._get_container_dataset_path(), 'mode': 'rw'}

        if len(self.task.known_datasets) > 0:
            for dataset_name, dataset_local_path in self.task.known_datasets.items():
                mount_command[dataset_local_path] = \
                    {'bind': join(self._get_container_dataset_path(), dataset_name), 'mode': 'ro'}

        # Build environments.
        env_command = []
        for env_name in env.keys():
            cmd = ["{}={}".format(env_name, env[env_name])]
            env_command += cmd

        # Build runtime command.
        runtime_command = "nvidia"

        # Build run command.
        command = ". /home/dcworker/.profile && conda activate deepcluster"
        if exists(requirements_file_host) and getsize(requirements_file_host) != 0:
            command += " && conda install --file {}".format(requirements_file_container)

        command += " && python {}".format(worker_run_path)
        self.worker_logger.log_info(
            "run",
            "container image: {}".format(self._get_container_image()))

        self.worker_logger.log_info(
            "run",
            "user command: {}".format(self.task.command))

        # Also take in rest of the container configurations.
        container_config = copy.deepcopy(container_config)
        container_config["volumes"] = mount_command
        container_config["detach"] = True
        container_config["user"] = DC_WORKER_USER_ID
        #container_config["network_disabled"] = True
        container_config["environment"] = env_command
        container_config["runtime"] = runtime_command
        container_config["working_dir"] = self._get_container_code_dir_location()
        docker_client = docker.from_env()
        exec_container = docker_client.containers.run(self._get_container_image(),
                                                      ["bash", "-c", command],
                                                      **container_config)

        return exec_container

    # --------------------------------------------------------------------------

    '''

        @abstract

            Expect:
                self.task_context: <TaskContext>
                self.task: <TrainingTask>

            Produce:
                None

            This routine will keep running until the user's code finishes, or
            server askes us to stop.

        @returns
            None - After the run stage, always go to post_run stage.

    '''

    def signal(self, simulate_keep_alive_response: Dict[str, Any] = None, is_signal_finish: bool = False):
        already_terminated = False
        alive = False
        graceful = False
        request_body = {}
        while True:
            if not already_terminated:
                alive, graceful = self.task_context.monitor()

            if alive and graceful:
                self.worker_logger.log_info(
                    "signal",
                    "worker is still running on task {}".format(
                        self._get_current_task_uuid()))

                request_body = {'task_uuid': self._get_current_task_uuid(),
                                'action': 'progress'}

                success, \
                status_code, \
                response_body, \
                error_message = request_server(
                    self.master_endpoint + "/api/v1/worker/task/",
                    'post',
                    **{"data": request_body,
                       "auth": self.auth_token})

                # if there is simulate_keep_alive_response
                # update corresponding values in the actual response
                if simulate_keep_alive_response is not None:
                    request_body.update(simulate_keep_alive_response)
                    # Set the status to success in simulated signal.
                    success = True
                    status_code = 200

                if not success:
                    self.worker_logger.log_error("signal", error_message)
                    # If the server has returned an unexpected response, there
                    # is really nothing can be done at the worker side other
                    # than signal kill the task process. Server will take care
                    # of the clean up.
                    self.worker_logger.log_info("signal", "worker status: stop")
                    self.task_context.terminate()
                    return

                if status_code == 200:
                    status = response_body.get("result", None)
                    create_tensorboard = response_body.get("create_tensorboard", None)
                    if status == "continue":
                        self.worker_logger.log_info(
                            "signal",
                            "worker status: continue")

                        if create_tensorboard:
                            self._create_tensorboard()

                        sleep(int(self.task.keep_alive_interval))
                        continue
                    else:
                        # Note that the server tells the work to stop, the worker
                        # does not need to signal finish.
                        if status != "stop":
                            self.worker_logger.log_warning(
                                "signal",
                                "unexpected worker status from server: {}".format(
                                    status))
                        else:
                            # Master does ask us to stop. Mark the task as finished
                            # as well as we don't need to report to master.
                            self._set_current_task_finished()

                        self.worker_logger.log_info(
                            "signal",
                            "terminate task {}".format(self._get_current_task_uuid()))

                        self.task_context.terminate()

                        # If server asks us to stop, it will pass along a
                        # PreSigned URL for uploading the output. Capture that.
                        self._get_output_upload_urls(response_body)
                        return
                elif status_code < 500:
                    self.worker_logger.log_warning(
                        "signal",
                        "unexpected response status: {}, error: {}".format(
                            status_code,
                            response_body.get("error", None)))

                    self.worker_logger.log_info(
                        "signal",
                        "terminate task {}".format(self._get_current_task_uuid()))

                    self.task_context.terminate()
                    return
                else:
                    # If server side has a problem, there is nothing more can
                    # be done at the client side. Abort the current job.
                    self.worker_logger.log_warning(
                        "signal",
                        "unexpected server side error status: {}".format(
                            status_code))

                    if self.task_context.can_retry():
                        self.worker_logger.log_info(
                            "signal",
                            "server side unexpected error, retry... (chance left: {})"
                                .format(self.task_context.retry_count))

                        sleep(int(self.task.keep_alive_interval))
                        continue
                    else:
                        self.worker_logger.log_info(
                            "signal",
                            "terminate task {}".format(self._get_current_task_uuid()))

                        self.task_context.terminate()
                        return
            else:
                # If the exec process has terminated already, check the output
                # queue to see if there is an item indicates that the task is
                # finished.
                already_terminated = True
                request_body = {}
                task_state = None
                if graceful:
                    self.worker_logger.log_info(
                        "signal",
                        "task {} finished".format(self._get_current_task_uuid()))

                    # If the worker needs to signal finish, let the server know
                    # the task has gracefuly finished. Note that there is no
                    # need to check the return status after this call.
                    if self.task.signal_finish:
                        task_state = 'finished'

                else:
                    self.worker_logger.log_warning(
                        "signal",
                        "task {} unexpectedly stopped".format(
                            self._get_current_task_uuid()))

                    # Let the server know the task has failed as the exec
                    # process unexpectedly terminated. Note that there is no
                    # need to check the return status after this call.
                    task_state = 'failed'

                success = True
                status_code = 0
                if not graceful or self.task.signal_finish:
                    if is_signal_finish:
                        success = True
                        status_code = 200
                    else:
                        success, \
                        status_code = self._report_server_task_state(task_state)

                self.task_context.terminate()
                if success and status_code >= 500:
                    # If server side has an error, retry.
                    if self.task_context.can_retry():
                        self.worker_logger.log_info(
                            "signal",
                            "server side unexpected error, retry... (chance left: {})"
                                .format(self.task_context.retry_count))

                        sleep(int(self.task.keep_alive_interval))
                        continue
                    else:
                        self.worker_logger.log_error(
                            "signal",
                            "server side unexpected error for too many times when siganl finish!")

                elif success and status_code < 300:
                    self.worker_logger.log_info(
                        "signal",
                        "successfully reported task {} finish to server!"
                            .format(self._get_current_task_uuid()))

                    # Mark the task as finished ONLY WHEN we successfully report
                    # that the task is finished to server.
                    self._set_current_task_finished()

                return

    def _report_server_task_state(self, task_state):
        if self._get_current_task_uuid() is None:
            self.worker_logger.log_error(
                "report_task_state",
                "fatal error! task_uuid is None!")

            return False, 500

        request_body = {'task_uuid': self._get_current_task_uuid(),
                        'action': task_state}

        success, status_code, response_body, _ = request_server(
            self.master_endpoint + "/api/v1/worker/task/",
            'post',
            **{"data": request_body,
               "auth": self.auth_token})

        if success and \
           response_body is not None:

            # If we tell server that we stopped, server will pass back a
            # PreSigned URL for uploading the output. Capture that.
            self._get_output_upload_urls(response_body)

        return success, status_code

    def _create_tensorboard(self):
        # Find an empty port that worker can use to create tensorboard
        # but there is a bug in tensorboard that cannot log event using port
        # other than 6006
        port = 6006

        # Start tensorboard
        self.task.tensorboard_process = \
            subprocess.Popen(["tensorboard", "--logdir={}".format(
                join(self.workdir, OUTPUT_DIR_NAME))])

        # Report tensorboard api back to master server
        request_body = {'tensorboard_created': 1}
        success, _, response_body, error_message = request_server(
            self.master_endpoint + "/api/v1/worker/task/{}/".format(
                self._get_current_task_uuid()),
            'put',
            **{"data": request_body,
               "auth": self.auth_token})
        if success:
            self.worker_logger.log_info(
                "tensorboard",
                "successfully started tensorboard at {}".format(
                    response_body.get("tensorboard_url", None)))
        else:
            self.worker_logger.log_warning(
                "tensorboard",
                "failed to start tensorboard with error: {}".format(
                    error_message))

        return

    def _get_output_upload_urls(self, response_body):
        if self.task is None:
            self.worker_logger.log_warning(
                "output_upload",
                "missing 'task_context'.")

            return

        self.task.output_upload_urls = None
        task_data = response_body.get("task_data", None)
        if task_data is None:
            self.worker_logger.log_warning(
                "output_upload",
                "server malformed response: missing 'task_data'.")

            return

        upload_urls = task_data.get("upload_urls", None)
        if upload_urls is None:
            self.worker_logger.log_warning(
                "output_upload",
                "server malformed response: missing 'upload_urls' inside 'task_data'.")

            return

        output_upload_urls = upload_urls.get(JOB_CONTENT_TYPE_OUTPUT, None)
        if output_upload_urls is None:
            self.worker_logger.log_warning(
                "output_upload",
                "server malformed response: missing '{}' inside 'task_data[upload_urls]'.".format(
                    JOB_CONTENT_TYPE_OUTPUT))

            return

        expected_fileds = ['url', 'fields']
        for expected_filed in expected_fileds:
            if expected_filed not in output_upload_urls:
                self.worker_logger.log_warning(
                    "output_upload",
                    "server malformed response: missing '{}' inside 'task_data[upload_urls][{}]'.".format(
                        expected_filed,
                        JOB_CONTENT_TYPE_OUTPUT))

                return

        self.worker_logger.log_info(
            "output_upload",
            "server responsed upload urls: {}.".format(output_upload_urls))

        self.task.output_upload_urls = output_upload_urls
        return

    # --------------------------------------------------------------------------

    '''

        @abstract

            Expect:
                self.task: <TrainingTask>
                user artifact inside /workdir/OUTPUT_DIR_NAME

            Produce:
                Upload the user artifact to S3.
                Upload the user logs to S3.
                Drop the refcount taken on the dataset and garbage collect
                if necessary.

        @returns
            None - post_run always go to cleanup.

    '''

    def post_run(self, simulate_need_upload_output: bool = False,
                 simulate_need_upload_log: bool = False,
                 local_output_folder: str = None):
        need_upload_output = simulate_need_upload_output \
            if simulate_need_upload_output is not None else False
        need_upload_log = simulate_need_upload_log \
            if simulate_need_upload_log is not None else False

        # Check if there is anything need to upload.
        for item in os.listdir(self._get_output_dir_location()):
            need_upload_output = True
            break

        if isfile(self._get_user_log_file()) and \
           getsize(self._get_user_log_file()) != 0:

            need_upload_log = True

        if need_upload_output or need_upload_log:
            self.worker_logger.log_info(
                "post_run",
                "task {} has artifacts need upload."
                    .format(self._get_current_task_uuid()))

            # First check if there is a local output folder. If not, ask server
            # for really uploading.
            if local_output_folder is not None:
                if need_upload_output:
                    shutil.copytree(self._get_output_dir_location(),
                                    join(local_output_folder, OUTPUT_DIR_NAME))

                if need_upload_log:
                    shutil.copyfile(self._get_user_log_file(),
                                    join(local_output_folder,
                                         self._get_user_log_file_name()))

            else:
                output_upload_urls = self.task.output_upload_urls
                if output_upload_urls is None:
                    self.worker_logger.log_error(
                        "post_run",
                        "do not have presigned url for uploading!")
                else:
                    if need_upload_output:
                        self._upload_to_presigned_url(
                                self._get_output_dir_location(),
                                self._get_upload_output_tar_location(),
                                self._get_upload_output_tar_file_name(),
                                output_upload_urls)

                    if need_upload_log:
                        self._upload_to_presigned_url(
                                self._get_log_dir_location(),
                                self._get_upload_log_tar_location(),
                                self._get_upload_log_tar_file_name(),
                                output_upload_urls)

        else:
            self.worker_logger.log_info(
                "post_run",
                "task {}: no training artifacts found".format(
                    self._get_current_task_uuid()))

        # try to clean up work dir after run
        if self.task.tensorboard_process is not None:
            try:
                self.tensorboard_process.kill()
            except Exception as e:
                self.worker_logger.log_error(
                    "post_run",
                    "failed to terminate tensorboard: {}".format(str(e)))

                traceback.print_exc()

        # Finally, drop the reference count on the dataset.
        self._unreference_dataset()
        return

    def _upload_to_presigned_url(self,
                                 upload_from,
                                 tar_location,
                                 upload_name,
                                 upload_urls):

        make_tarfile(tar_location, upload_from)
        # Sanity check that tar file exists.
        if not isfile(tar_location):
            self.worker_logger.log_warning(
                "upload",
                "failed to tar {} at {}".format(upload_from, tar_location))

            return False

        with open(tar_location,'rb') as fd:
            files = {'file': (upload_name, fd)}
            response = requests.post(upload_urls["url"],
                                     data=upload_urls["fields"],
                                     files=files)
            if not response.ok:
                self.worker_logger.log_warning(
                    "upload",
                    "failed to upload tar {} to {}".format(
                        tar_location,
                        upload_urls["url"]))

                return False

        return True

    # --------------------------------------------------------------------------

    '''

        @abstract

            Expect:
                None

            Produce:
                Anything under self.workdir is cleared.
                self.task set to None.
                self.task_uuid set to None.

        @returns
            success:
                - success <bool>: Whether successfully finished this stage.

    '''

    def task_cleanup(self):
        # First clean up the workdir.
        self._cleanup_workdir()

        # If there is a task uuid, this means the worker has polled a task.
        # If the task is *not* marked as finished, this means the worker
        # encountered some fatal error in the handling and **has not reported
        # to master that it cannot handle the task**.  In this case, we must
        # attempt to report failure to master.
        success = True
        if self._get_current_task_uuid() is not None and \
                not self._get_current_task_finished():

            self.worker_logger.log_warning(
                "cleanup",
                "task: {} is not marked as finished, attempt to report failure to master"
                    .format(self._get_current_task_uuid()))

            try:
                # The task must be reported as failed if we reach here and
                # have not marked the task has finished.
                success, status_code = self._report_server_task_state('failed')
                if not success or status_code >= 300:
                    self.worker_logger.log_error(
                        "cleanup",
                        "task: {} failed to report to master: success: {} status: {}"
                            .format(self._get_current_task_uuid(),
                                    success,
                                    status_code))

                    success = False
            except Exception as e:
                self.worker_logger.log_error(
                    "cleanup",
                    "task: {} exception when report to master: {}"
                        .format(self._get_current_task_uuid(),
                                str(e)))

                traceback.print_exc()
                success = False

        elif self._get_current_task_uuid() is None:
            self.worker_logger.log_warning(
                "cleanup",
                "no task is present for this worker...")

        else:
            self.worker_logger.log_info(
                "cleanup",
                "task: {} completed!".format(
                    self._get_current_task_uuid()))

        self.task = None
        self.task_uuid = None
        return success

    # --------------------------------------------------------------------------

    def _get_code_dir_location(self):
        return join(self.workdir, CODE_DIR_NAME)

    def _get_output_dir_location(self):
        return join(self.workdir, OUTPUT_DIR_NAME)

    def _get_log_dir_location(self):
        return join(self.workdir, LOG_DIR_NAME)

    def _get_dataset_local_path(self, dataset_name):
        return join(self.toplevel_datadir, dataset_name)

    def _get_upload_log_tar_file_name(self):
        return "log_{}{}".format(self.task_uuid[:6], EXTENSION_TAR_GZ)

    def _get_upload_log_tar_location(self):
        return join(self.workdir,
                    self._get_upload_log_tar_file_name())

    def _get_upload_output_tar_file_name(self):
        return "output_{}{}".format(self.task_uuid[:6], EXTENSION_TAR_GZ)

    def _get_upload_output_tar_location(self):
        return join(self.workdir,
                    self._get_upload_output_tar_file_name())

    def _get_container_code_dir_location(self):
        return CONTAINER_CODE_DIR_LOCATION

    def _get_container_output_dir_location(self):
        return CONTAINER_OUTPUT_DIR_LOCATION

    def _get_container_log_dir_location(self):
        return CONTAINER_LOG_DIR_LOCATION

    def _get_container_dataset_path(self):
        return CONTAINER_DATASET_DIR_LOCATION

    def _get_container_image(self):
        return self.task.container_image

    def _get_container_image_name(self):
        image_name = self._get_container_image()
        if ":" not in image_name:
            return image_name
        else:
            return image_name.split(":")[0]

    def _get_container_image_tag(self):
        image_name = self._get_container_image()
        if ":" not in image_name:
            return None
        else:
            return image_name.split(":")[1]

    def _get_user_log_file_name(self):
        return "{}.log".format(self._get_current_task_uuid())

    def _get_user_log_file(self):
        return join(self._get_log_dir_location(),
                    self._get_user_log_file_name())

    def _cleanup_workdir(self):
        delete_all_from_dir(self.workdir)
        return

    def _get_current_task_uuid(self):
        return self.task_uuid

    def _get_current_job_uuid(self):
        if self.task is None:
            return None
        return self.task.job_uuid

    def _get_current_task_finished(self):
        if self.task is None:
            return False

        return self.task.finished

    def _set_current_task_finished(self):
        if self.task:
            self.task.finished = True
        return

    def _get_provisioned_worker_worker_run_path(self):
        return PROVISIONED_WORKER_WORKER_RUN_PATH

