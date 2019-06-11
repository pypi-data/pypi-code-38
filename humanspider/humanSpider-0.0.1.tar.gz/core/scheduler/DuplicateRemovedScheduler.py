from abc import abstractmethod
from bloom_filter import BloomFilter
from core.scheduler.Scheduler import Scheduler


class DuplicateRemovedScheduler(Scheduler):

    def __init__(self):
        self._remover = BloomFilter(max_elements=10000, error_rate=0.001)

    def put(self, request, again=False):
        if again:
            self.should_add_scheduler(request)
        elif request.method is "POST":
            self.should_add_scheduler(request)
        elif self.in_filter(request.hash()):
            return
        else:
            self.should_add_scheduler(request)

    @property
    def remover(self):
        return self._remover

    @remover.setter
    def remover(self, remover):
        self._remover = remover

    def in_filter(self, request_hash):
        """ 默认-布隆过滤器去重 """
        if request_hash in self._remover:
            return True
        else:
            self._remover.add(request_hash)
            return False

    @abstractmethod
    def should_add_scheduler(self, request):
        """ 实际的入队列操作 """
