from celery import Celery  # default Celery App Class
from celery.exceptions import Ignore
from CustomApp import CustomBackendCalls
from uuid import uuid4
import sys

sys.path.append("..")

app = Celery('tasks_test')
app.config_from_object('config')  # will load config of celery

backend_object = None

"""
    test script (deprecated)
"""


@app.task(bind=True, base=CustomBackendCalls)
def test_backend_objects(self):
    global backend_object
    backend_object = self
    worker_id = str(uuid4())
    print("test 1")
    test_machine_register(worker_id)
    print("test 2")
    test_update_heartbeat(worker_id)

    # test related to tasks
    print("test 3")
    test_insert_new_task()
    print("test 4")
    object_locked = test_lock_the_task(0)
    task_id = object_locked[1]
    meta = object_locked[2]

    print("test 5")
    test_update_status(task_id, 1)
    print("test 6")
    test_update_error(task_id, 999)
    print("test 7")
    test_get_status(task_id)
    print("test 8")
    test_set_worker(task_id, worker_id)

    # bulk test
    print("test 9")
    test_bulk_insert_task(10)
    print("test 10")
    test_bulk_lock(10)

    print("test 11")
    test_get_unprocessed_job_count(0)

    sample_result = "Hello Test"
    import hashlib
    checksum = hashlib.sha256(sample_result.encode("utf-8")).hexdigest()
    print("test 12")
    test_insert_result(task_id, {"file": sample_result}, 0, b'0', checksum)
    print("test 13")
    test_get_result(task_id)
    print("test 14")
    test_compare_checksum(checksum)

    print("test 15")
    test_get_master_jobs(1, None)

    raise Ignore


# t1
def test_machine_register(worker_id):
    """
    this function is to test the machine registry
    :param worker_id: id of the worker
    :return:
    """
    backend_object.register_machine(worker_id, "192.168.1.4", jobtype=0, meta="")
    print("Machine registered successfully")


# t2
def test_update_heartbeat(worker_id):
    """

    :param worker_id:
    :return:
    """
    backend_object.update_heartbeat(worker_id)
    print("Machine heartbear updated successfully")


# t3
def test_insert_new_task():
    """

    :return:
    """
    meta = {"test_key": "test_value"}
    backend_object.insert_new_task(meta, jobtype=0)


# t4
def test_lock_the_task(jobtype):
    """

    :param jobtype:
    :return:
    """
    return_object = backend_object.lock_the_task(jobtype=jobtype)
    print(return_object)
    if return_object[0]:
        print("lock test successful")
        return return_object


# t5
def test_update_status(task_id, new_status):
    """

    :param task_id:
    :param new_status:
    :return:
    """
    backend_object.update_task_status(task_id, new_status)
    print("status update test successful")


# t6
def test_update_error(task_id, error_id):
    """

    :param task_id:
    :param error_id:
    :return:
    """
    if backend_object.update_error_id(task_id, error_id):
        print("update error id test successful")


# t7
def test_get_status(task_id):
    """

    :param task_id:
    :return:
    """
    return_object = backend_object.get_task_status(task_id)
    print(return_object)
    print("get status test successful")


# t8
def test_set_worker(task_id, worker_id):
    """

    :param task_id:
    :param worker_id:
    :return:
    """
    if backend_object.set_worker_for_task(task_id, worker_id):
        print("worker id test successful")


# t9
def test_bulk_insert_task(count):
    """

    :param count:
    :return:
    """
    if count > 100:
        print("Warning :Max insert is limited to 100")
        return None
    meta = {"test_key": "test_value"}
    meta_list = []
    for i in range(0, count):
        meta_list.append(meta)
    return_object = backend_object.bulk_insert_new_task(meta_list, 0)
    if return_object is True:
        print("Bulk insert test sucessful")
        return None
    print("Bulk insert test failed")


# t10
def test_bulk_lock(count):
    """

    :param count:
    :return:
    """
    is_locked, lock_objects = backend_object.bulk_lock_task(0, 10)
    if is_locked is True:
        for lock_object in lock_objects:
            print(lock_object[0], lock_object[1], sep=' | ')


# t11
def test_get_unprocessed_job_count(jobtype):
    """

    :param jobtype:
    :return:
    """
    count = backend_object.get_unprocessed_job_count(0)
    if count:
        print(count)


# t12
def test_insert_result(task_id, meta, jobtype, binary_object, checksum):
    """
    this function is used to insert result into result table.
    :param task_id: id of the task
    :param meta: meta contains all the job info in it
    :param jobtype: type of the job
    :param binary_object:
    :param checksum: checksum to handle duplication
    :return:
    """
    backend_object.insert_result(task_id, meta, jobtype, binary_object, checksum)


# t13
def test_get_result(task_id):
    """

    :param task_id:
    :return:
    """
    return_object = backend_object.get_result(task_id)
    print(return_object)


# t14
def test_compare_checksum(checksum):
    """
    used to test calculated checksum
    :param checksum:
    :return:
    """
    return_object = backend_object.compare_checksum(checksum)
    print(return_object)


# t15
def test_get_master_jobs(jobtype, ticker_filter):
    """
    this function is used to get jobs from master table
    :param jobtype: type of the job (urlfetch, datafetch, apifetch)
    :param ticker_filter:
    :return:
    """
    is_done, master_jobs = backend_object.get_master_jobs(jobtype, ticker_filter)
    if is_done:
        for master_job in master_jobs:
            print(master_job[0], master_job[1], sep='|')
        print("master jobs test successful")
