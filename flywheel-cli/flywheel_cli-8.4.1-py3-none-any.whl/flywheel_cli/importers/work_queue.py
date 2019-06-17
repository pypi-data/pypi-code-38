import heapq
import itertools
import logging
import threading
import tempfile

import fs.filesize

from abc import ABC, abstractmethod

log = logging.getLogger(__name__)

from abc import ABC, abstractmethod

class Task(ABC):
    def __init__(self, group):
        self.group = group
        self.skipped = False

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def get_bytes_processed(self):
        pass

    @abstractmethod
    def get_desc(self):
        pass

    def allow_retry(self):
        return False

class WorkQueue(object):
    """Multi-threaded upload queue that reports progress"""
    def __init__(self, groups):
        """Initialize the work queue

        Arguments:
            groups (list): List of tuples of group tag to maximum concurrent jobs per group
        """
        # Queue of waiting jobs, by group
        self.waiting = {key: [] for key in groups.keys()}
        # Queue of pending jobs
        self.pending = []
        # Queue of completed jobs
        self.completed = []
        # List of errored jobs
        self.errors = []
        # Count of skipped jobs
        self.skipped = { group: 0 for group in groups.keys() }

        self.groups = groups

        self.running = False
        self._finish_called = False

        self._lock = threading.RLock()
        self._cond = { group: threading.Condition(self._lock) for group in groups.keys() }
        self._complete_cond = threading.Condition()

        self._work_threads = []
        self._counter = itertools.count()

    def start(self):
        self.running = True
        self._finish_called = False

        for group, count in self.groups.items():
            work_fn = self._work_fn(group)
            tname = '{}-worker'.format(group)

            for i in range(count):
                t = threading.Thread(target=work_fn, name=tname)
                t.daemon = True
                t.start()
                self._work_threads.append(t)

    def enqueue(self, task, priority=10):
        cond = self._cond[task.group]
        with cond:
            count = next(self._counter)
            heapq.heappush(self.waiting[task.group], (priority, count, task))
            cond.notify()

    def skip_task(self, task=None, group=None):
        if group is None:
            group = task.group
        with self._lock:
            self.skipped[group] += 1

    def take(self, group):
        result = None
        cond = self._cond[group]
        with cond:
            while self.running:
                queue = self.waiting[group]
                if queue:
                    _, _, result = heapq.heappop(queue)
                    break
                cond.wait()

            if not self.running:
                return None

            self.pending.append(result)
            return result

    def complete(self, task):
        finished = False

        with self._lock:
            self.pending.remove(task)
            self.completed.append(task)

            if self._finish_called:
                # Check to see if we're done
                finished = not self.tasks_pending()

        if finished:
            with self._complete_cond:
                self._complete_cond.notify_all()

    def log_exception(self, job, exc_info):
        with self._lock:
            log.error('%s Error: %s', job.get_desc(), str(exc_info))
            log.debug('Details:', exc_info=exc_info)

    def has_errors(self):
        with self._lock:
            return bool(self.errors)

    def error(self, task):
        finished = False

        with self._lock:
            self.pending.remove(task)
            self.errors.append(task)

            if self._finish_called:
                # Check to see if we're done
                finished = not self.tasks_pending()

        if finished:
            with self._complete_cond:
                self._complete_cond.notify_all()

    def tasks_pending(self):
        with self._lock:
            if self.pending:
                return True

            for queue in self.waiting.values():
                if queue:
                    return True
            return False

    def get_stats(self):
        results = {}

        with self._lock:
            for group in self.groups.keys():
                results[group] = {
                    'completed': 0,
                    'completed_bytes': 0,
                    'skipped': self.skipped[group]
                }

            for task in self.completed:
                stats = results[task.group]
                stats['completed'] = stats['completed'] + 1
                stats['completed_bytes'] = stats['completed_bytes'] + task.get_bytes_processed()

            for task in self.pending:
                stats = results[task.group]
                stats['completed_bytes'] = stats['completed_bytes'] + task.get_bytes_processed()

        return results

    def requeue_errors(self):
        errors = []
        with self._lock:
            self._finish_called = False
            errors = self.errors
            self.errors = []

        for job in errors:
            self.enqueue(job)

    def wait_for_finish(self):
        with self._complete_cond:
            self._finish_called = True

            while self.running and self.tasks_pending():
                self._complete_cond.wait(timeout=0.2)

    def shutdown(self):
        # Shutdown
        self.running = False
        for cond in self._cond.values():
            with cond:
                cond.notify_all()

        # Wait for threads
        for t in self._work_threads:
            t.join()

        self._work_threads = []

    def _work_fn(self, group):
        def do_work():
            self._do_work(group)
        return do_work

    def _do_work(self, group):
        while True:
            job = self.take(group)
            if not job:
                return # Shutdown

            try:
                next_job, priority = job.execute()
            except Exception as ex:
                # Add to errors list
                self.log_exception(job, ex)
                self.error(job)
                continue

            if next_job:
                self.enqueue(next_job, priority=priority)

            # Complete the job
            self.complete(job)

