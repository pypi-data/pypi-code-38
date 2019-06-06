# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)
import queue
import time
import logging
logger = logging.getLogger("dativa.tools.aws.queue")


class RetryException(Exception):
    def __init__(self, reason):
        Exception.__init__(self, 'The task exceeded the retry limit: {0}'.format(reason))
        self.reason = reason


class Task:
    """
    An abstraction representing a Single task
    """

    def __init__(self, name, arguments):
        self.is_complete = False
        self.error = None
        self.arguments = arguments
        self.id = None
        self.retries = 0
        self.name = name


class TaskQueue:
    """
    This is an abstract class that contains all required common functionality to
    support implementation of queues in aws client libraries.
    Two separate queues are maintained:
    active_queue - Only tasks in this queue are allowed to run.
                   Once tasks are completed they are removed from this queue.
                   No of tasks in active queue <= max_size.
    pending_queue - Contains tasks that are awaiting execution.
                    Tasks from pending_queue are added to active_queue in FIFO
                    fashion.
    """
    
    def __init__(self, max_size, retry_limit=3, max_tasks_same_name=1024):
        self.pending_tasks = queue.Queue()
        self.active_queue = []
        self.max_size = max_size
        self.retry_limit = retry_limit
        self.max_tasks_same_name = max_tasks_same_name

    def add_task(self, name, args):
        """This method adds a tasks to the pending_tasks queue"""
        task = Task(name, args)
        self.pending_tasks.put(task)
        self._empty_active_queue()
        self._fill_active_queue()
        return task

    def _empty_active_queue(self):
        """
        Removes completed task from active queue and populates freed spots with tasks
        in the front of pending_tasks queue
        """
        # Remove completed tasks from active queue
        for index, task in enumerate(self.active_queue):
            self._update_task_status(task)
            if task.error:
                if task.retries < self.retry_limit:
                    logger.info("Retrying job {0}, previously raised error with error {1}".
                                format(task.name, task.error))
                    task.retries += 1
                    task.error = None
                    self._trigger_task(task)
                else:
                    task.is_complete = True
                    self.active_queue.pop(index)
                    raise RetryException("{0} [name: '{1}', id: {2}]".format(
                                         task.error, task.name, task.id))

            if task.is_complete:
                if task.error:
                    logger.error("Task failed: ID {0}, error is {1}".format(task.id, task.error))
                else:
                    logger.debug("Task is complete: ID {0}".format(task.id))
                self.active_queue.pop(index)

    def _running_jobs(self, job_name):
        """
        Return the number of concurrent jobs
        """
        running_jobs = 0
        for each_job in self.active_queue:
            if each_job.name == job_name:
                running_jobs += 1
        return running_jobs

    @property
    def number_active(self):
        return len(self.active_queue)

    @property
    def number_pending(self):
        return self.pending_tasks.qsize()

    def _fill_active_queue(self):
        # Add add tasks to active queue if size of queue is less the max query limit
        for i in range(0, self.max_size - self.number_active):
            if not(self.pending_tasks.empty()):
                task = self.pending_tasks.get()
                if self._running_jobs(task.name) < self.max_tasks_same_name:
                    self.active_queue.append(task)
                    self._trigger_task(task)
                else:
                    # put to the back of the queue
                    self.pending_tasks.put(task)
            else:
                break

    def wait_for_completion(self):
        """
        This method runs until execution of all tasks is completed
        """
        while len(self.active_queue):
            logging.info("{} tasks are awaiting exection".format(self.number_active))
            self._empty_active_queue()
            self._fill_active_queue()
            time.sleep(10)

    def _trigger_task(self, task):
        """
           This function should implement functionality to start aws task
           Once triggered is_active should be set to True
        """
        raise NotImplementedError("must be implemented by subclass")

    def _update_task_status(self, task):
        """Updates task status and returns updated task object
           Also handles retries
        """
        raise NotImplementedError("must be implemented by subclass")

    def _empty_pending_queue(self):
        """
        Empty pending queue of tasks - prevent them from being run
        :return: None
        """
        while not self.pending_tasks.empty():
            self.pending_tasks.get()
