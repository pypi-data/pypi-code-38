from ioflow.task_manager.local_task_manager import LocalTaskManager
from ioflow.task_manager.db_task_manager import DbTaskManager

task_manager_class_registry = {}


def get_task_manager_class(config):
    return task_manager_class_registry[config.get('task_manager_schema', 'local')]


def registry_task_manager_class(schema, class_):
    task_manager_class_registry[schema] = class_


registry_task_manager_class('local', LocalTaskManager)
registry_task_manager_class('db', DbTaskManager)
