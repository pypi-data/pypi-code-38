from ioflow.task_manager.task_manager import TaskManager
from ioflow.task_manager.status_controller.db_status_controller import DbStatusController


class DbTaskManager(TaskManager):
    def __init__(self, *args, **kwargs):
        super(DbTaskManager, self).__init__(DbStatusController(*args, **kwargs))
