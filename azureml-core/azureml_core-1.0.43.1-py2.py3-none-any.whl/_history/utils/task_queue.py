# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
from six.moves import queue
import threading

from azureml._history.utils.async_task import AsyncTask
from azureml._history.utils.log_scope import LogScope


class TaskQueue(object):
    """
    A class for managing async tasks
    """
    def __init__(self, ident, logger,
                 num_workers=1,
                 error_handler=None):
        self._logger = logger.getChild(ident)
        # self._logger.debug = lambda s: print("DEBUG: {}".format(s))
        self._work_queue = queue.PriorityQueue()
        # For right now, don't need queue for errors, but it's
        # probable that we'll want the error handler looping on queue thread
        self._error_queue = queue.Queue()
        self._err_handler = error_handler
        self._finished = False
        self._workers = {}
        for i in range(num_workers):
            _name, thread = TaskQueue.create_and_start_worker(self._awaiter, ident, i)
            self._workers[_name] = thread

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    @staticmethod
    def create_and_start_worker(func, root_name, ident):
        _name = "{0}.worker_{1}".format(root_name, ident)
        thread = threading.Thread(target=func, name=_name)
        thread.start()
        return _name, thread

    def _awaiter(self):
        while True:
            priority, task = self._work_queue.get()
            self._logger.debug("Got task: {}".format(task))
            if task is None:
                self._work_queue.task_done()
                break

            _id = task.ident()
            try:
                self._logger.debug("Calling Task {0}".format(_id))
                result = task.wait()
                self._logger.debug("Finished Task {0}: {1}".format(_id, result))
            except Exception as err:
                self._logger.error("Failed to wait on Task {0}: {1}".format(_id, err))
                self._error_queue.put(err)

                # Now that we have an error queue, drop the below and simplify the API?
                if self._err_handler:
                    self._err_handler(err)
            finally:
                self._work_queue.task_done()

    def add(self, async_task, priority=None):
        '''Blocking, no timeout add task to queue'''
        if self._finished:
            raise AssertionError("Cannot add task to finished queue")
        if not isinstance(async_task, AsyncTask):
            raise ValueError("Can only add AsyncTask, got {0}".format(type(async_task)))

        entry = (priority, async_task)
        if priority is None:
            priority = 100
        self._logger.debug("Adding task {0} to queue with priority {1}".format(async_task.ident(), priority))
        self._work_queue.put(entry)
        self._logger.debug("Queue size is approx. {}".format(self._work_queue.qsize()))
        # self.complete_requests()

    def flush(self, source=None):
        num_messages = self._work_queue.qsize()
        with LogScope(self._logger, "WaitFlush"):
            self._work_queue.join()
        self._logger.debug("Finished flushing approx. {} messages. Source={}".format(num_messages, source))

    def finish(self):
        '''Flushes queue and waits for all workers to return'''
        if self._finished:
            return
        self.flush()
        # Put a None in the queue to kill the true loops in the workers
        worker_statuses = [(_id, worker.is_alive()) for _id, worker in self._workers.items()]
        for _ in worker_statuses:
            self._work_queue.put((float("inf"), None))

        # Join those threads back here
        for _id, worker in self._workers.items():
            with LogScope(self._logger, "WaitWorker{0}".format(_id)):
                worker.join()

        self._logger.debug("Waiting for queue to empty: {0}".format(self._work_queue.queue))
        self._work_queue.join()
        self._finished = True
        self._logger.debug("Finished calling finish")

    def errors(self):
        '''Returns a copy of all exceptions seen in the queue'''
        if not self._finished:
            raise AssertionError("Can't get errors on unfinished TaskQueue")

        errs = copy.deepcopy(self._error_queue.queue)
        return [e for e in errs]
