from ioflow.task_manager.db_task_manager import DbTaskManager

import tensorflow as tf


class DbTaskManagerHook(tf.train.SessionRunHook):
    def __init__(self, *args, **kwargs):
        self.task_manager = DbTaskManager(*args, **kwargs)

    def before_run(self, *args, **kwargs):
        self.task_manager.wait()

    def after_run(self, run_context, run_values):
        if self.task_manager.should_stop():
            run_context.request_stop()
