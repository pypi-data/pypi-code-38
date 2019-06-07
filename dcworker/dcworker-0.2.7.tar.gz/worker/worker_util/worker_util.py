import errno
import hashlib
import tarfile
from time import sleep

import requests
import shutil
import json
from os import listdir
from os.path import isfile, join, exists
import os

from common.global_variable import TF_CONFIG, CODE_DIR_NAME, OUTPUT_DIR_NAME
from common.util.s3_utils import create_s3_client, upload_dir_to_s3, upload_file_to_s3


class WorkQueueItem(object):
    item_type = None
    context = None

    def __init__(self, item_type, context):
        self.item_type = item_type
        self.context = context


class WorkerFinishQueueItem(WorkQueueItem):
    def __init__(self):
        super().__init__("signal_finish", None)


class WorkerFailureQueueItem(WorkQueueItem):
    def __init__(self, exception):
        super().__init__("signal_failure", exception)


def get_tasks(pid):
    r = os.popen('tasklist /v').read().strip().split('\n')
    for i in range(len(r)):
        if pid in r[i]:
            return r[i]
    return []


def is_process_running(pid):
    r = get_tasks(str(pid))
    if not r:
        # process is existed
        return "finished"
    elif 'Not Responding' in r:
        # hanging
        return "failed"
    else:
        # running
        return "running"


def signal_worker_finish(task_uuid, auth_token, master_endpoint):
    request_body = {'task_uuid': task_uuid, 'action': 'finished'}
    while True:
        r = requests.post(master_endpoint + "/api/v1/worker/task/", data=request_body, auth=auth_token)

        if r.text:
            response_body = json.loads(r.text)
        else:
            raise RuntimeError("worker::signal_task_completion server failed to return any response")

        if r.status_code == 200:
            break
        elif r.status_code < 500:
            raise RuntimeError(
                "worker::signal_task_completion fail to report exec process finish with status code {0}. error: {1}"
                    .format(r.status_code, response_body.get("error")))
        else:
            # failed to report finish to master server
            sleep(10)

    print("task {0} is finished".format(task_uuid))


def latest_checkpoint_from_s3(bucket_name, checkpoint_location, client):
    bucket = client.list_objects_v2(Bucket=bucket_name, Prefix=checkpoint_location)
    assert bucket is not None
    meta = []
    meta_extension = ".meta"
    for f in bucket["Contents"]:
        filename, file_extension = os.path.splitext(os.path.basename(f["Key"]))
        if file_extension == meta_extension:
            meta.append(filename)

    return "s3://{0}/{1}/{2}".format(bucket_name, checkpoint_location, max(meta) + meta_extension)


def latest_checkpoint_from_local(checkpoint_location):
    meta = []
    meta_extension = ".meta"
    for f in listdir(checkpoint_location):
        if isfile(join(checkpoint_location, f)):
            filename, file_extension = os.path.splitext(os.path.basename(f))
            if file_extension == meta_extension:
                meta.append(filename)

    return join(checkpoint_location, max(meta) + meta_extension)


def download_file_from_s3(bucket_name, code_location, dest_dir, client):
    bucket = client.list_objects_v2(Bucket=bucket_name, Prefix=code_location)
    assert bucket is not None
    if "Contents" not in bucket:
        raise RuntimeError("worker::download_file_from_s3 code location is empty")

    for f in bucket["Contents"]:
        if os.path.basename(f["Key"]) != '':
            client.download_file(bucket_name, f["Key"],
                                 join(dest_dir, os.path.basename(f["Key"])))


def get_worker_uuid():
    register_location = "./"
    worker_uuid = None
    for f in listdir(register_location):
        if isfile(join(register_location, f)):
            filename, file_extension = os.path.splitext(os.path.basename(f))
            if filename.startswith("register_") and file_extension == ".json":
                if worker_uuid is None:
                    worker_uuid = filename[9:]
                else:
                    raise RuntimeError("find more than one worker register file")

    return worker_uuid


# convert str into dict
def json_loads(string):
    return json.loads(str(string).replace("'", '"'))


def worker_prepare_gpu(worker_type, resource_id):
    if worker_type != "gpu" or resource_id < 0:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(resource_id)
    return


# create tf_config for each server
def create_tf_config(job_name, task_index, cluster_spec):
    worker_list = cluster_spec["worker"]
    ps_list = cluster_spec["ps"]
    cluster = {"chief": [worker_list[0]], "worker": worker_list[1:], "ps": ps_list}
    tf_config = {"cluster": cluster}

    job_type = "worker"
    if job_name == "ps":
        job_type = "ps"
    elif task_index == 0:
        job_type = "chief"
    else:
        # worker index starts from 0
        task_index -= 1

    tf_config["task"] = {"type": job_type, "index": task_index}

    # set the TF_CONFIG in the env variable
    os.environ[TF_CONFIG] = str(tf_config).replace("'", '"')
    print("job_name: {}, task_index: {}, tf_config: {}".format(job_name, task_index, tf_config))


def upload_output(src, dest, s3_temp_token):
    if exists(src):
        if not exists(dest):
            client = create_s3_client(s3_temp_token)
            bucket_name = s3_temp_token['s3_bucket_name']
            _ = upload_dir_to_s3(src, bucket_name, OUTPUT_DIR_NAME, dest, client)
        else:
            out_dir = join(dest, OUTPUT_DIR_NAME)
            if exists(out_dir):
                shutil.rmtree(out_dir)
            # this is local testing case:
            shutil.copytree(src, out_dir)
    else:
        raise RuntimeError("cannot find output folder in {}".format(src))


def upload_log(log_file_location, job_id, s3_temp_token):
    if exists(log_file_location):
        if not exists(job_id):
            client = create_s3_client(s3_temp_token)
            bucket_name = s3_temp_token['s3_bucket_name']
            s3_path = "{0}/{1}".format(job_id, OUTPUT_DIR_NAME)
            _ = upload_file_to_s3(log_file_location, bucket_name, s3_path, client)
        else:
            out_dir = join(job_id, OUTPUT_DIR_NAME)
            if exists(out_dir):
                shutil.rmtree(out_dir)
            # this is local testing case:
            shutil.copytree(log_file_location, out_dir)
    else:
        raise RuntimeError("cannot find output folder in {}".format(log_file_location))
