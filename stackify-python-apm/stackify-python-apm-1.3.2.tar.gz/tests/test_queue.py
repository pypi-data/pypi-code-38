import time
from unittest import TestCase
try:
    import Queue as queue
except ImportError:
    import queue

from stackifyapm.queue import QueueData
from stackifyapm.queue import QueueListener


class QueueDataTest(TestCase):

    def test_queue_data_creation(self):
        queue_data = QueueData(record='some_record', delay=0)

        assert queue_data.started
        assert queue_data.record == 'some_record'
        assert queue_data.delay == 0

    def test_queue_data_creation_with_delay(self):
        queue_data = QueueData(record='some_record', delay=10)

        assert queue_data.started
        assert queue_data.record == 'some_record'
        assert queue_data.delay == 10


class QueueHandlerClassMock(object):
    called = False

    def handler(self, record, delay):
        self.called = True


class QueueListenerTest(TestCase):

    def test_queue_listener_creation(self):
        _queue = queue.Queue(10)
        queue_handler = QueueHandlerClassMock()

        queue_listener = QueueListener(_queue, queue_handler.handler)

        assert queue_listener.queue == _queue
        assert queue_listener.handler == queue_handler.handler

    def test_queue_listener_enqueue(self):
        _queue = queue.Queue(10)
        queue_handler = QueueHandlerClassMock()
        queue_listener = QueueListener(_queue, queue_handler.handler)

        queue_listener.enqueue('some_data')

        assert _queue.qsize() == 1

    def test_queue_listener_dequeue(self):
        _queue = queue.Queue(10)
        queue_handler = QueueHandlerClassMock()
        queue_listener = QueueListener(_queue, queue_handler.handler)
        queue_listener.enqueue('some_data')

        queue_data = queue_listener.dequeue(False)

        assert isinstance(queue_data, QueueData)
        assert queue_data.record == 'some_data'

    def test_queue_listener_start(self):
        _queue = queue.Queue(10)
        queue_handler = QueueHandlerClassMock()
        queue_listener = QueueListener(_queue, queue_handler.handler)
        queue_listener.enqueue('some_data', delay=1)

        queue_listener.start()

        assert queue_listener._thread

    def test_queue_listener_stop(self):
        _queue = queue.Queue(10)
        queue_handler = QueueHandlerClassMock()
        queue_listener = QueueListener(_queue, queue_handler.handler)
        queue_listener.start()

        queue_listener.stop()
        time.sleep(.5)

        assert not queue_listener._thread

    def test_queue_listener_handler_with_0_delay(self):
        _queue = queue.Queue(10)
        queue_handler = QueueHandlerClassMock()
        queue_listener = QueueListener(_queue, queue_handler.handler)
        queue_listener.enqueue('some_data', delay=0)

        queue_listener.start()
        time.sleep(.5)

        assert queue_handler.called

    def test_queue_listener_handler_with_1_delay(self):
        _queue = queue.Queue(10)
        queue_handler = QueueHandlerClassMock()
        queue_listener = QueueListener(_queue, queue_handler.handler)
        queue_listener.enqueue('some_data', delay=1)

        queue_listener.start()
        time.sleep(1.5)

        assert queue_handler.called
