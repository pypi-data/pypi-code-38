from ioflow.task_manager.task_manager import TaskManager
from ioflow.task_manager.status_controller.local_status_controller import LocalStatusController


class LocalTaskManager(TaskManager):
    def __init__(self, *args, **kwargs):
        super(LocalTaskManager, self).__init__(LocalStatusController())
