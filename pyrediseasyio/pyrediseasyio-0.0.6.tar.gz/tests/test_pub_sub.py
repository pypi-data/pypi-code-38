import unittest
import time
import threading

from pyrediseasyio.reader_writer import ReaderWriter
from assertpy import assert_that


class PubSubTests(unittest.TestCase):

    def _publish_many(self, count: int, wait: float = 0):
        if wait > 0:
            time.sleep(wait)
        for i in range(0, count):
            self.pubsub1.publish(f"Message {i}")

    def setUp(self):
        self.pubsub1 = ReaderWriter(channel="Channel1")
        self.pubsub2 = ReaderWriter(channel="Channel1")
        self.pubsub1.flush_keys()
        self.pubsub2.flush_keys()

    def test_get_single_message(self):
        pubsub1, pubsub2 = self.pubsub1, self.pubsub2
        r = pubsub2.get_next_message()
        assert_that(r).is_none()
        data = "This is a test"
        pubsub1.publish(data)
        c, d = pubsub2.get_next_message()
        assert_that(c).is_equal_to("Channel1")
        assert_that(d).is_equal_to(data)

    def test_get_many_messages(self):
        count = 2
        pubsub1, pubsub2 = self.pubsub1, self.pubsub2
        self._publish_many(count)
        time.sleep(0.2)
        messages = pubsub2.get_messages()
        assert_that(len(messages)).is_equal_to(count)
        messages = pubsub2.get_messages()
        assert_that(messages).is_empty()

    def test_listen_for_messages(self):
        pubsub1, pubsub2 = self.pubsub1, self.pubsub2
        threading.Thread(target=self._publish_many, args=(20, 0.1)).start()
        messages = []
        for i, m in enumerate(pubsub2.listen()):
            if i >= 10:
                break
            messages.append(m[1])
        assert_that(len(messages)).is_equal_to(10)

