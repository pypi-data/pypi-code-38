from ioflow.task_manager import get_task_manager_class
from ioflow.hooks.task_manager import TaskManagerHook


def get_task_manager_hook(config):
    task_manager_class = get_task_manager_class(config)
    task_manager = task_manager_class(config=config)

    return TaskManagerHook(task_manager)
