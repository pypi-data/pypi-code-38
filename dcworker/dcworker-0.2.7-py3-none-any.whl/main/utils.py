import os.path
import socket, errno
import uuid
from typing import Dict, Any

import yaml
import shutil

from worker.worker_start import Worker

from common.dbinterface import *
from common.global_variable import *
from common.util.common_utils import *

from worker.worker_runtime import (RUNTIME_GPU_INFO,
                                   RUNTIME_SYSTEM_INFO,
                                   WORKER_MACHINE_DEEPCLUSTER_STANDARD,
                                   WORKER_MACHINE_PROVISIONED,
                                   WorkerRuntime)

###############################################################################

GPU_REGISTER_FILE_NAME = "gpu_register.yaml"
GPU_REGISTER_FILE_GPU_UUIDS_KEY = "register_gpus"

GPU_FAKE_UUID = "GPU-Fake"
GPU_FAKE_INFO = {
    "fake_id": {
        "gpu_name": "GPU-Fake",
        "driver_version": "GPU-Fake-Driver",
        "pcie.link.gen.current": 0,
        "pcie.link.gen.max": 0,
        "pcie.link.width.current": 0,
        "pcie.link.width.max": 0,
        "memory.total": 0
    }
}

DDL_DEFAULT_LOG_FOLDER_NAME = "default"

###############################################################################

def gpu_uuid_to_gpu_id(worker_runtime, gpu_uuid):
    if worker_runtime.fake_gpu():
        return True, -1

    if gpu_uuid in worker_runtime.runtime[RUNTIME_GPU_INFO]:
        return True, worker_runtime.runtime[RUNTIME_GPU_INFO][gpu_uuid]["index"]
    else:
        return False, None

def gpu_uuids_get_gpu_ids(worker_runtime, gpu_uuids):
    gpu_uuids_ids = []
    for gpu_uuid in gpu_uuids:
        success, gpu_id = gpu_uuid_to_gpu_id(worker_runtime, gpu_uuid)
        if not success:
            continue
        gpu_uuids_ids += [(gpu_uuid, gpu_id)]
    return gpu_uuids_ids

def get_worker_info(worker_runtime, gpu_uuid):
    worker_info = {}
    worker_info["system_info"] = worker_runtime.runtime[RUNTIME_SYSTEM_INFO]
    gpu_info = {}
    if gpu_uuid in worker_runtime.runtime[RUNTIME_GPU_INFO]:
        for gpu_id, info in worker_runtime.runtime[RUNTIME_GPU_INFO].items():
            gpu_info[gpu_id] = info

    elif gpu_uuid == GPU_FAKE_UUID:
        gpu_info = GPU_FAKE_INFO
    else:
        return None
    worker_info["sharing"] = worker_runtime.get_gpu_sharing()
    worker_info["gpu_info"] = gpu_info
    return worker_info

###############################################################################

def register_single_worker(toplevel_workdir,
                           master_server,
                           base_port,
                           task_uuid):
    port = base_port
    worker_num = 0
    while True:
        worker_workdir_name = "worker{}".format(worker_num)
        worker_workdir = os.path.join(toplevel_workdir, worker_workdir_name)
        if os.path.exists(worker_workdir):
            worker_num += 1
            continue
        os.mkdir(worker_workdir)
        break
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            if port >= 65535:
                print("[Error] invalid port number: {}".format(port))
                return False, None, None, None, None

            s.bind(("127.0.0.1", port))
            s.close()
            print("[Register] found available port: {}".format(port))
            break
        except socket.error as e:
            port = ((port // 100) + 1) * 100
            if e.errno == errno.EADDRINUSE:
                continue
            else:
                # something else raised the socket.error exception
                print("[Error] {}".format(e))
                return False, None, None, None, None
        except Exception as e:
            print("[Error] uncaught error: {}".format(str(e)))
            return False, None, None, None, None

    register_is_success, \
    worker_uuid, \
    worker_passcode = Worker.register(master_server, task_uuid)
    if not register_is_success:
        print("[Error] worker failed to register")
        return False, None, None, None, None

    print("[Register] registered worker {}".format(worker_uuid))
    return True, worker_uuid, worker_passcode, worker_workdir, port


def register(runtime: WorkerRuntime,
             metadir: str,
             toplevel_workdir: str,
             num_worker_per_gpu: int,
             task_uuid: str = None):
    """
    Register worker in local database only
    Args:
        runtime: worker runtime
        metadir: local meta dir that host GPU yaml information
        toplevel_workdir: local work dir for this worker
        num_worker_per_gpu: number of GPU in this worker
        task_uuid: affinity task uuid

    Returns:
        Indicates if the local registration is successful
    """

    # First, check if the GPU register file exists. Note that if running in CPU mode for
    # local debugging, then GPU register file is not required.
    gpu_register_file = os.path.join(metadir, GPU_REGISTER_FILE_NAME)
    if not runtime.fake_gpu():
        if not os.path.exists(gpu_register_file):
            print("[Error::FATAL] Does not have a GPU register file. Cannot register workers.")
            return False

        # Parse the GPU register file to understand which GPUs should be registered.
        try:
            with open(gpu_register_file, "r") as f:
                gpu_register = yaml.load(f)
        except Exception as e:
            print("[Error::FATAL] Cannot parse GPU register file: {}".format(str(e)))
            return False

        # Validate the GPUs.
        gpu_uuids = gpu_register.get(GPU_REGISTER_FILE_GPU_UUIDS_KEY, None)
        if not gpu_uuids:
            print("[Error::FATAL] Do not have GPU for registration.")
            return False

        gpu_uuids_ids = gpu_uuids_get_gpu_ids(runtime, gpu_uuids)
        gpu_count = len(gpu_uuids_ids)
        if gpu_count == 0:
            print("[Error::FATAL] None of the registered GPUs is valid anymore.")
            return False
    else:
        # For local testing, fake to have 1 GPU.
        gpu_uuids_ids = [(GPU_FAKE_UUID, -1)]
        gpu_count = 1

    if num_worker_per_gpu < 1 or num_worker_per_gpu > 8:
        print('[Error::FATAL] GPU sharing must between 1 and 8.')
        return False

    # Create the table that contains worker registration information.
    if runtime.get_worker_machine_type() == WORKER_MACHINE_DEEPCLUSTER_STANDARD:
        success, _ = create_table(WORKER_REGISTRATION_TABLE_COMMAND)
        if not success:
            print("[Error::FATAL] Failed to create worker registration table.")
            return False

    master_server = runtime.master_server()
    print("Start worker registration")
    print("\t[master_server url]: {}".format(master_server))
    print("\t[toplevel working directory]: {}".format(toplevel_workdir))
    print("\t[meta directory]: {}".format(metadir))
    print("\t[task_uuid] : {}".format(task_uuid))
    print("\t[worker per gpu] : {}".format(num_worker_per_gpu))

    port = 10000
    worker_registered = {}
    # Register all the workers.
    for (gpu_uuid, gpu_id) in gpu_uuids_ids:
        for i in range(0, num_worker_per_gpu):
            success, \
            worker_uuid, \
            worker_passcode, \
            worker_workdir, \
            worker_port = register_single_worker(
                            toplevel_workdir,
                            master_server,
                            port,
                            task_uuid)

            if not success:
                continue

            # Keep track of the registered worker in the db.
            worker_config = (worker_uuid,
                             worker_passcode,
                             worker_workdir,
                             str(worker_port),
                             gpu_uuid,)

            save_worker_registration(runtime, worker_config)
            port = ((worker_port // 100) + 1) * 100
            if port >= 65535:
                print("[Error] Running out of port! Abort further registration!")
                break

    return True


def registered(runtime):
    if runtime.get_worker_machine_type() == WORKER_MACHINE_DEEPCLUSTER_STANDARD:
        # If there exists the worker registration table, then the workers have
        # been registered.
        success, exists = table_exists(WORKER_REGISTRATION_TABLE_NAME)

        # If the database is not available for some reason, it is fatal...
        if not success:
            print("[Error::FATAL] Cannot connect to DB server. Abort...")
            return False, None
        else:
            return True, exists
    else:
        return True, False


def unregister(runtime, toplevel_workdir):
    if runtime.get_worker_machine_type() == WORKER_MACHINE_DEEPCLUSTER_STANDARD:
        # Drop the worker registration table if exists.
        success, exists = table_exists(WORKER_REGISTRATION_TABLE_NAME)

        # If the database is not available for some reason, it is fatal...
        if success and exists:
            success, _ = drop_table(WORKER_REGISTRATION_TABLE_NAME)
            if not success:
                print("[Error::FATAL] Cannot drop the worker registration table!")
                return False

    # Purge the work dir.
    shutil.rmtree(toplevel_workdir, ignore_errors=True)
    return True


def get_registered_workers(runtime) -> Dict[str, Any]:
    if runtime.get_worker_machine_type() == WORKER_MACHINE_DEEPCLUSTER_STANDARD:
        """
        get worker register information from worker local pg
        :return: a dict of worker registration information
        """
        success, worker_configs = query_from_table(WORKER_QUERY_REGIDTRATION_COMMAND)
    else:
        worker_configs = runtime.get_worker_registration()

    registerd_workers = {}
    for (worker_uuid, passcode, workdir, port, gpu_uuid) in worker_configs:
        registerd_workers[worker_uuid] = {
            'passcode': passcode,
            'workdir': workdir,
            'port': port,
            'gpu_uuid': gpu_uuid
        }

    return registerd_workers


def save_worker_registration(runtime, config):
    if runtime.get_worker_machine_type() == WORKER_MACHINE_DEEPCLUSTER_STANDARD:
        execute_query_on_table(WORKER_REGISTER_COMMAND, values=config)
    else:
        runtime.save_worker_registration(config)

    return

###############################################################################

def cleanup_datasets(datadir):
    success, exists = table_exists(DATASET_TABLE_NAME)
    if not success:
        print("[Error::FATAL] Cannot connect to DB server. Abort...")
        return False

    if not exists:
        # If there exists no dataset table, delete everything from the datadir.
        delete_all_from_dir(datadir)

        # Create a dataset table.
        success, _ = create_table(DATASET_TABLE_COMMAND)
        if not success:
            print("[Error::FATAL] Failed to create dataset table.")
            return False

        return True
    else:
        # If there is a dataset table, for each entry in the table, check if
        # they are still valid.
        success, datasets = query_from_table(DATASET_QUERY_ALL_COMMAND)
        if not success:
            print("[Error::FATAL] Cannot connect to DB server. Abort...")
            return False

        for (dataset_name, \
             local_path, \
             dataset_persist, \
             dataset_ready, \
             refcount) in datasets:

            delete_local_dir = False
            delete_db_entry = False
            print("[Dataset::INFO] {} (Local: {}) p: {}, r: {}, c: {}".format(
                    dataset_name,
                    local_path,
                    dataset_persist,
                    dataset_ready,
                    refcount))

            # If the dataset is not in a ready state, there cannot be anyone
            # downloading for it anymore. Clear both the local dir and the db
            # entry.
            if dataset_ready == 0:
                delete_local_dir = True
                delete_db_entry = True

            # For each non-persisted dataset, there cannot be any worker
            # depending on it at fresh start. Clear both the local dir and the
            # db entry.
            if dataset_persist == 0:
                delete_local_dir = True
                delete_db_entry = True

            # If the local_path no longer exists, clear the db entry.
            if not os.path.isdir(local_path):
                delete_db_entry = True

            # Ignore failure here as this is best effort.
            if delete_db_entry:
                delete_from_table(DATASET_DELETE_COMMAND, values=(dataset_name, ))

            if delete_local_dir:
                if os.path.isdir(local_path):
                    shutil.rmtree(local_path, ignore_errors=True)

        return True