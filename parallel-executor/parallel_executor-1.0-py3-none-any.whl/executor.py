import threading
import queue
from datetime import datetime
from .states import States
from .info import Info
from .task import Task
from .errors import AddTaskAfterStartError

class Executor:
    def __init__(self, queue_size=0, worker_threads=1, tasks=[]):
        self._queue_size = queue_size
        self._worker_threads = worker_threads
        self._tasks = tasks
        self._queue = queue.Queue(maxsize = queue_size)
        self._state = States.NOT_STARTED
        self._started_timestamp = None

    def addTask(self, task):
        if self._state == States.NOT_STARTED:
            self._tasks.append(task)
        else:
            raise AddTaskAfterStartError

    def getState(self):
        return self._state

    def isCompleted(self):
        return self._state == States.COMPLETED

    def getTasks(self):
        return self._tasks

    def getTasksCount(self):
        return len(self._tasks)

    def getInfo(self):
        return Info.getInfo(self._tasks, self._started_timestamp)

    def _worker(self):
        while(self._state == States.RUNNING):
            if self._state == States.COMPLETED:
                break

            if not self._queue.empty(): 
                task = self._queue.get()
                task()
                self._queue.task_done()

    def _producer(self):
        for task in self._tasks:
            self._queue.put(task)

    def _observer(self):
        while(self._state != States.COMPLETED):
            completed = True
            for task in self._tasks:
                if task.getStatus() != Task.Status.COMPLETED:
                    completed = False
                    break

            if completed == True:
                self._state = States.COMPLETED

    def executeTasks(self):
        self._started_timestamp = datetime.now()
        self._state = States.RUNNING
        threads = []

        # Run workers
        for i in range(self._worker_threads):
            worker = threading.Thread(name='Worker thread' + str(i), target=self._worker, args=())
            threads.append(worker)
            worker.start()

        # Put tasks to queue
        producer_thread = threading.Thread(name='Producer thread', target=self._producer, args=())
        producer_thread.start()

        # Create observer
        observer_thread = threading.Thread(name='Observer thread', target=self._observer, args=())
        observer_thread.start()

        # Wait for threads to complete
        producer_thread.join()
        observer_thread.join()
        for thread in threads:
            thread.join()
