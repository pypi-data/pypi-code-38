from ioflow.task_manager.task_manager_base import TaskManagerBase

import tensorflow as tf


class TaskManagerHook(tf.train.SessionRunHook):
    def __init__(self, task_manager: TaskManagerBase):
        self.task_manager = task_manager

    def before_run(self, *args, **kwargs):
        self.task_manager.wait()

    def after_run(self, run_context, run_values):
        if self.task_manager.should_stop():
            run_context.request_stop()
