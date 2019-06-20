from threading import Thread
from six.moves.queue import Queue

NUM_THREAD = 32


class ParralizedClient(object):
    def __init__(self, base_client, timeout_per_call=3):
        self._client = base_client
        self._queue = Queue()
        self._workers = tuple(ClientGetWorker(client=self,
                                              queue=self._queue)
                              for _ in range(NUM_THREAD))
        self.timeout_per_call = timeout_per_call
        for w in self._workers:
            w.start()

    def get(self, *args, **kwargs):
        return self._client.get(*args, **kwargs)

    def _defer_action_on_client(self, action_on_client):
        task = Task(action_on_client=action_on_client)
        self._queue.put(task)
        return task.result

    def multiget(self, paths):
        worker_results = list(map(lambda path:
                                  self._defer_action_on_client(lambda client: client.get(path)),
                                  paths))

        total_timeout = self.timeout_per_call * max(1, len(worker_results))
        timeout_on_blocking_call(lambda: self._queue.join(), timeout=total_timeout)

        return [worker_result.get_or_fail() for worker_result in worker_results]

    def put(self, *args, **kwargs):
        return self._client.put(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self._client.post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._client.delete(*args, **kwargs)


def timeout_on_blocking_call(blocking_call, timeout):
    thread = Thread(target=blocking_call)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        raise RuntimeError('Timeout')


class WorkerResult(object):
    def __init__(self):
        self._result = None
        self._error = None

    def get_or_fail(self):
        if self._error:
            raise self._error
        return self._result

    def save_execution(self, action):
        try:
            self._result = action()
        except BaseException as e:
            self._error = e


class Task(object):
    def __init__(self, action_on_client):
        self.result = WorkerResult()
        self.action_on_client = action_on_client

    def run(self, client):
        self.result.save_execution(lambda: self.action_on_client(client))


class ClientGetWorker(Thread):
    def __init__(self, client, queue):
        Thread.__init__(self)
        self.daemon = True
        self._client = client
        self._queue = queue

    def run(self):
        while True:
            task = self._queue.get()
            task.run(self._client)
            self._queue.task_done()
