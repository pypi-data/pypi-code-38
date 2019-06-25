from schedule.utils.log.TaskLogger import TaskLogger


class ILogAbleHandler:
    def __init__(self):
        self._task_logger = None

    @property
    def task_logger(self)->TaskLogger:
        "日志记录方法,有两个方法: log(message) 以及 error(exception)"
        return self._task_logger or TaskLogger(None)

    @task_logger.setter
    def task_logger(self, value:TaskLogger):
        self._task_logger = value