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
        while(True):
            task = self._queue.get()
            if task is None:
                break
            task()            
            self._queue.task_done()

    def _producer(self):
        for task in self._tasks:
            self._queue.put(task)
        
        # Wait untill all tasks are done        
        self._queue.join()

        # Stop the workers        
        for i in range(self._worker_threads):
            self._queue.put(None)

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

        # Wait for threads to complete
        for thread in threads:
            thread.join()
        producer_thread.join()
        self._state = States.COMPLETED

