import threading
import time
try:
    import Queue as queue
except ImportError:
    import queue


from stackifyapm.conf.constants import QUEUE_TIME_INTERVAL_IN_MS


class QueueData(object):
    def __init__(self, record=None, delay=0):
        self.started = time.time()
        self.record = record
        self.delay = delay

    def __repr__(self):
        return '{} {}'.format(self.record.id, self.delay)


class QueueListener(object):

    def __init__(self, queue, handler):
        self.queue = queue
        self.handler = handler

        self._stop = None
        self._thread = None

    def start(self):
        self._stop = threading.Event()
        self._thread = t = threading.Thread(target=self._monitor)
        t.setDaemon(True)
        t.start()

    def stop(self):
        self._stop = None
        self._thread = None
        self._clean_up()

    def started(self):
        return self._stop and not self._stop.isSet()

    def prepare(self, record, delay=0):
        return QueueData(record=record, delay=delay)

    def enqueue(self, record, delay=0):
        queue_record = isinstance(record, QueueData) and record or self.prepare(record, delay)
        self.queue.put_nowait(queue_record)

    def dequeue(self, block):
        return self.queue.get(block)

    def handle(self, queue_record):
        self.handler(queue_record.record, queue_record.delay)

    def _monitor(self):
        q = self.queue
        has_task_done = hasattr(q, 'task_done')
        while self._stop and not self._stop.isSet():
            try:
                queue_record = self.dequeue(False)

                if time.time() - queue_record.started > queue_record.delay:
                    self.handle(queue_record)
                else:
                    self.enqueue(queue_record)

                if has_task_done:
                    q.task_done()

                time.sleep(QUEUE_TIME_INTERVAL_IN_MS / 1000)
            except queue.Empty:
                self.stop()

    def _clean_up(self):
        # making sure we are logging all done transaction in queue
        q = self.queue
        has_task_done = hasattr(q, 'task_done')
        while True:
            try:
                queue_record = self.dequeue(False)

                self.handle(queue_record)

                if has_task_done:
                    q.task_done()

            except queue.Empty:
                break
