import json
import os
import sys
import traceback
from os.path import join, exists
import subprocess
from subprocess import Popen
from typing import Dict, Any

###############################################################################

# global variables
_WORKER_RUN_ENV_TASK_UUID = "TASK_UUID"
_WORKER_RUN_ENV_TASK_INDEX = "TASK_INDEX"
_WORKER_RUN_ENV_TASK_CLUSTER_SPEC = "CLUSTER_SPEC"
_WORKER_RUN_ENV_TASK_ROLE = "TASK_ROLE"
_WORKER_RUN_ENV_WORKER_TYPE = "WORKER_TYPE"
_WORKER_RUN_ENV_WORKER_RESOURCE_ID = "RESOURCE_ID"
_WORKER_RUN_ENV_DATASET_DIR = "DATASET"
_WORKER_RUN_ENV_CODE_DIR = "CODE"
_WORKER_RUN_ENV_OUTPUT_DIR = "OUTPUT"
_WORKER_RUN_ENV_LOG_DIR = "LOG"
_WORKER_RUN_ENV_COMMAND = "COMMAND"

_WORKER_FAILED_MARKER = "worker_run_failed"
_TF_CONFIG = 'TF_CONFIG'
_PYTHON_PATH = "PYTHONPATH"


###############################################################################

def worker_prepare_gpu(worker_type, resource_id):
    if worker_type == "gpu" or resource_id >= 0:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(resource_id)

    return


def prepare_distributed_training(task_role, task_index, cluster_spec):
    worker_list = cluster_spec["worker"]
    ps_list = cluster_spec["ps"]
    cluster = {}
    cluster["chief"] = [worker_list[0]]
    cluster["worker"] = worker_list[1:]
    cluster["ps"] = ps_list
    tf_config = {
        "cluster": cluster
    }

    job_type = "worker"
    if task_role == "ps":
        job_type = "ps"
    elif task_index == 0:
        job_type = "chief"
    else:
        # worker index starts from 0
        task_index -= 1

    tf_config["task"] = {"type": job_type, "index": task_index}

    # set the TF_CONFIG in the env variable
    os.environ[_TF_CONFIG] = str(tf_config).replace("'", '"')
    print("task_role: {}, task_index: {}, tf_config: {}".format(task_role, task_index, tf_config))


def chmod_dir(path, mode):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in [os.path.join(root, d) for d in dirs]:
            os.chmod(dir, mode)

        for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, mode)


def execute_command(cmd: str, user_stdout: Dict[str, Any]):
    subprocess.call(cmd, stdout=user_stdout, stderr=user_stdout, shell=True)


def worker_run():
    log_dir = None
    try:
        dataset_dir = os.getenv(_WORKER_RUN_ENV_DATASET_DIR)
        output_dir = os.getenv(_WORKER_RUN_ENV_OUTPUT_DIR)
        code_dir = os.getenv(_WORKER_RUN_ENV_CODE_DIR)
        log_dir = os.getenv(_WORKER_RUN_ENV_LOG_DIR)
        task_uuid = os.getenv(_WORKER_RUN_ENV_TASK_UUID)
        task_role = os.getenv(_WORKER_RUN_ENV_TASK_ROLE)
        task_index = int(os.getenv(_WORKER_RUN_ENV_TASK_INDEX))
        worker_type = os.getenv(_WORKER_RUN_ENV_WORKER_TYPE)
        resource_id = int(os.getenv(_WORKER_RUN_ENV_WORKER_RESOURCE_ID))
        cluster_spec = json.loads(os.getenv(_WORKER_RUN_ENV_TASK_CLUSTER_SPEC))
        command = json.loads(os.getenv(_WORKER_RUN_ENV_COMMAND))

        print("Structure:")
        print(" - Dataset folder location: {}".format(dataset_dir))
        print(" - Code folder location: {}".format(code_dir))
        print(" - Output folder location: {}".format(output_dir))
        print(" - Log folder location: {}".format(log_dir))
        print("Task parameters:")
        print(" - task_uuid: {}".format(task_uuid))
        print(" - task_role: {}".format(task_role))
        print(" - task_index: {}".format(task_index))
        print(" - cluster_spec: {}".format(cluster_spec))
        print(" - worker_type: {}".format(worker_type))
        print(" - resource_id: {}".format(resource_id))

        # Env variables passed to the user subprocess
        os.environ[_WORKER_RUN_ENV_DATASET_DIR] = dataset_dir
        os.environ[_WORKER_RUN_ENV_OUTPUT_DIR] = output_dir
        os.environ[_PYTHON_PATH] = code_dir

        # Prepare for distributed training mode.
        if task_index != -1:
            print("Distributed training mode")
            prepare_distributed_training(task_role, task_index, cluster_spec)
        else:
            print("Single worker training mode")

        worker_prepare_gpu(worker_type, resource_id)
        # Create files for user output.
        user_stdout = open(join(log_dir, "{}.log".format(task_uuid)), "w")
    except Exception as e:
        print("Exception occured: {}".format(e))
        traceback.print_exc()
        if exists(log_dir):
            with open(join(log_dir, _WORKER_FAILED_MARKER), "w") as f:
                f.write(str(e))

        return

    try:
        # Starting at this point, redirect the stdout and stderr to log file
        # to pass out the user's outputs.
        if isinstance(command, list):
            for cmd in command:
                execute_command(cmd, user_stdout)
        else:
            execute_command(command, user_stdout)

        # Finally, make sure the files generated are accessible from outside.
        chmod_dir(output_dir, 0o776)
        chmod_dir(log_dir, 0o776)
    except:
        traceback.print_exc()
    finally:
        if user_stdout is not None:
            user_stdout.close()


if __name__ == '__main__':
    worker_run()
