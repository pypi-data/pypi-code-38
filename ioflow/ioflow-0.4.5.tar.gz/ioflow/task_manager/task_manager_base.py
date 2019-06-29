class TaskManagerBase(object):
    def __init__(self):
        pass

    def should_stop(self) -> bool:
        """
        return True if task_manager is requested to stop task,
        otherwise will return false
        :return: bool
        """
        raise NotADirectoryError

    def wait(self):
        """
        this method will block if task_manager is requested to pause task,
        otherwise will return immediately, return value is not defined yet
        """
        raise NotADirectoryError
