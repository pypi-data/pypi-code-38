from celery import task
from tasks_test import test_backend_objects
from uuid import uuid4

backend_object = test_backend_objects

if __name__ == '__main__':
    """
        This is for just testing.
    """
    task_id = str(uuid4())
    jobtype = 0
    meta = {"task_id": task_id, "jobtype": jobtype}
    test_backend_objects.apply_async((), task_id=task_id)
    test_backend_objects.apply_async((), task_id=task_id, queue="q0001")
