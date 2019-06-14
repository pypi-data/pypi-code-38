from __future__ import (absolute_import, division, print_function, unicode_literals)

import logging
from queue import Queue as pyQueue
from threading import Thread

logger = logging.getLogger(__name__)


class Queue(pyQueue):
    def __init__(self, name, pipeline=None, maxsize=0, output_queue=None):
        super(Queue, self).__init__(maxsize=maxsize)
        self.name = name
        self.output_queue = output_queue
        self.pipeline = pipeline

    def set_output_queue(self, output_queue):
        self.output_queue = output_queue

    def start(self):
        logger.info('queue: name=%s processing is started, output name=%s', self.name,
                    getattr(self.output_queue, 'name', None))
        while True:
            if self.pipeline:
                logger.info('stats: %s', self.pipeline.get_progress())
            received_data = self.get()
            if received_data is None:
                logger.info('queue: name=%s receive stop signal', self.name)
                if self.output_queue:
                    self.output_queue.put(received_data)
                break
            len_received_data = len(received_data)
            logger.info('queue: name=%s start to process data threads=%s', self.name, len_received_data)
            tab = []
            pool = []
            for i in range(len_received_data):
                methods, data = received_data[i]
                if data:
                    t = Thread(target=methods[0], args=(methods[1:], data, pool))
                    t.start()
                    tab.append(t)
            self.task_done()
            for t in tab:
                t.join()
            if self.output_queue:
                self.output_queue.put(pool)
            logger.info('queue: name=%s end portion from %s threads', self.name, len_received_data)


class Pipeline(object):
    def __init__(self):
        self._list = []
        self._threads = []

    def add_worker(self, name, maxsize=0):
        q = Queue(name=name, pipeline=self, maxsize=maxsize)
        if self._list:
            self._list[-1].set_output_queue(q)
        self._list.append(q)

    def start(self):
        for q in self._list:
            thread = Thread(target=q.start, args=())
            thread.start()
            self._threads.append(thread)

    def stop(self):
        self.put(None)

    def put(self, data):
        if not self._list:
            raise ValueError('add some queues before putting elements to pipeline')
        self._list[0].put(data)
        if data is None:
            for t in self._threads:
                t.join()

    def get_progress(self):
        stats = []
        for q in self._list:
            stats.append('name: {}={}/{}'.format(q.name, q.qsize(), q.maxsize))
        return ' '.join(stats)
