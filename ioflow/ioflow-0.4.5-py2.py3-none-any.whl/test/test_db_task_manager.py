import sys
import time

from ioflow.task_manager.db_task_manager import DbTaskManager


def fake_client(task_manager):
    for _ in range(600):
        task_manager.wait()
        time.sleep(1)
        print("I am working pre 1s")
        if task_manager.should_stop():
            print("I am stopped")
            sys.exit(0)

    print("I quit as normal")


config = {
    'task_id': '5d0b7ad5b775fa16367a2f8d',
    'task_info_url': 'http://api-algorithm.ecarx.ai/dbservice//train/queryTaskById'
}
task_manager = DbTaskManager(config=config)

fake_client(task_manager)
