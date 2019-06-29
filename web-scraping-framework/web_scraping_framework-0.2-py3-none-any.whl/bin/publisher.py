from traceback import format_exc
import time
import requests
import json
import sys
from tasks import urlfetch_task
from tasks import datafetch_task
from tasks import apifetch_task

from tasks import defaultTask  # added inorder make Database Operation through celery object

# TODO need to be multi threaded
# for multi lock mechanism and update status to added queue
# bulk update

defaultTask.apply_async()

backend_object = defaultTask
jobtypes = [1, 2, 3]  # 0001, 0002
max_queue_count = 200
max_bulk_objects = 50


def msg_queue_api_call(queue_name, option_value):  # get current Queue Length
    """
    Will return current Queue i.e. Pending Task from RabbitMQ
    :param queue_name: queue name
    :param option_value: option values. like length, messages.
    :return:
        [True, value] -> on successful execution
        OR
        [False, None] -> if execution failed.
    """
    try:
        r = requests.get('http://localhost:15672/api/queues', auth=('admin', 'nimda'))
        #  feature request need config from database
        data = json.loads(r.text)
        for d in data:
            if d['name'] == queue_name:
                return [True, d[option_value]]
        return [False, None]
    except Exception as e:
        print(format_exc())
        return [False, None]


def publish_tasks(jobtype, is_test=False):
    """
    This function will publish task in queue.
    :param jobtype: unique ID for group of jobs
    :param is_test: is testing flag.
    :return:
        True -> on successful execution
        OR
        False -> if execution failed
    """
    is_unprocessed_job_count, unprocessed_job_count = backend_object.get_unprocessed_job_count(jobtype)
    if is_unprocessed_job_count:
        print("Unprocessed job count {0} for jobtype {1}".format(str(unprocessed_job_count), str(jobtype)))
        if int(unprocessed_job_count) == 0:
            return False
    else:
        print("Problem with finding unprocessed job count")
        return False
    is_worker_count, worker_count = msg_queue_api_call("q" + str(jobtype).zfill(4), 'consumers')
    if is_worker_count:
        if worker_count == 0:
            print("NO WORKER AVAILABLE FOR JOBTYPE {0}".format(str(jobtype).zfill(4)))
            return False
    is_queue_count, current_queue_count = msg_queue_api_call("q" + str(jobtype).zfill(4), 'messages')
    if is_queue_count:
        print("Queue count for jobtype {0} is {1}".format(str(jobtype).zfill(4), str(current_queue_count)))
        max_iterations = 1
        fill_count = 0
        is_queue_greater = False
        if is_test is False:
            if max_queue_count > current_queue_count:
                fill_count = max_queue_count - current_queue_count
                if unprocessed_job_count < fill_count:
                    fill_count = unprocessed_job_count
                max_iterations = round(fill_count / max_bulk_objects)
            else:
                max_iterations = 0
                is_queue_greater = True
        if is_test is True:
            max_iterations = 1
        if max_iterations == 0 and unprocessed_job_count != 0:
            max_iterations = 1
        if is_queue_greater:
            max_iterations = 0

        for i in range(0, max_iterations):
            is_elements_lock = False
            lock_objects = None
            if is_test:
                is_elements_lock, lock_objects = backend_object.bulk_lock_task(jobtype, 1)
            else:
                is_elements_lock, lock_objects = backend_object.bulk_lock_task(jobtype, max_bulk_objects)
            if is_elements_lock:
                # Add task_id in meta
                for lock_object in lock_objects:
                    task_id = lock_object[0]
                    meta = lock_object[1]
                    meta["task_id"] = task_id
                    meta["jobtype"] = jobtype
                    if jobtype == int("0001"):
                        urlfetch_task.apply_async((meta,), task_id=task_id, queue="q" + str(jobtype).zfill(4))
                    elif jobtype == int("0002"):
                        datafetch_task.apply_async((meta,), task_id=task_id, queue="q" + str(jobtype).zfill(4))
                    elif jobtype == int("0003"):
                        apifetch_task.apply_async((meta,), task_id=task_id, queue="q" + str(jobtype).zfill(4))
                    print("Inserted task into queue.. Task id :", task_id)
            if is_test:
                print("Stopping test condition")
                sys.exit(0)
            # else:
            #    print("Can not lock the task.")
    print("{0} , {1} , {2} , {3} , {4} , {5} ".format(str(max_queue_count), str(current_queue_count), str(fill_count),
                                                      str(max_iterations), str(unprocessed_job_count),
                                                      str(jobtype).zfill(4)))


if __name__ == '__main__':
    """
        Usage :
            python publisher.py <is_test_flag>
            
        Example :
            1. with is_test_flag :
                $ python publisher.py test
            2. without is_test_flag :
                $ python publisher.py    
    """
    is_test = False
    try:
        arg1 = sys.argv[1]
        if arg1 == "test":
            is_test = True
        else:
            is_test = False
    except Exception as e:
        pass

    while 1:
        for jobtype in jobtypes:
            try:
                print("test condition is {0}".format(str(is_test)))
                publish_tasks(jobtype, is_test)
            except Exception as e:
                print("problem in publisher please look into it")
                print(format_exc())
            time.sleep(1)
        time.sleep(2)
