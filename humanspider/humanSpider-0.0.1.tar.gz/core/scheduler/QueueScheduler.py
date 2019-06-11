from queue import Queue
from queue import Empty

from core.scheduler.DuplicateRemovedScheduler import DuplicateRemovedScheduler


class QueueScheduler(DuplicateRemovedScheduler):
    def __init__(self):
        super().__init__()
        self.queue = Queue()

    def should_add_scheduler(self, request):
        # 不加锁的方式下往队列里加任务
        self.queue.put(request, block=False)

    def get(self):
        try:
            res = self.queue.get(block=False)
            return res
        except Empty:
            return None

    def get_queue_size(self):
        return self.queue.qsize()

    def close(self):
        self.queue = Queue()
