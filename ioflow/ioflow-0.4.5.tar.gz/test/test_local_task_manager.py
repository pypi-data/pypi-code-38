import sys
import time

from ioflow.task_manager.local_task_manager import LocalTaskManager


def fake_client(task_manager):
    for _ in range(60):
        task_manager.wait()
        time.sleep(1)
        print("I am working pre 1s")
        if task_manager.should_stop():
            print("I am stopped")
            sys.exit(0)

    print("I quit as normal")


task_manager = LocalTaskManager()

fake_client(task_manager)
