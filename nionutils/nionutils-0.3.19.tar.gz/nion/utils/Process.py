"""
Utility classes for implementing task queues and sets.
"""

# standard libraries
import copy
import queue
import threading

# third party libraries
# None

# local libraries
# None


class TaskQueue(queue.Queue):

    def perform_tasks(self):
        # perform any pending operations
        qsize = self.qsize()
        while not self.empty() and qsize > 0:
            try:
                task = self.get(False)
            except queue.Empty:
                pass
            else:
                task()
                self.task_done()
            qsize -= 1

    def clear_tasks(self):
        # perform any pending operations
        qsize = self.qsize()
        while not self.empty() and qsize > 0:
            try:
                task = self.get(False)
            except queue.Empty:
                pass
            else:
                self.task_done()
            qsize -= 1


# keeps a set of tasks to do when perform_tasks is called.
# each task is associated with a key. overwriting a key
# will discard any task currently associated with that key.
class TaskSet(object):
    def __init__(self):
        self.__task_dict = dict()
        self.__task_dict_mutex = threading.RLock()
    def add_task(self, key, task):
        with self.__task_dict_mutex:
            self.__task_dict[key] = task
    def clear_task(self, key):
        with self.__task_dict_mutex:
            if key in self.__task_dict:
                self.__task_dict.pop(key, None)
    def perform_tasks(self):
        with self.__task_dict_mutex:
            task_dict = copy.copy(self.__task_dict)
            self.__task_dict.clear()
        for task in task_dict.values():
            task()
