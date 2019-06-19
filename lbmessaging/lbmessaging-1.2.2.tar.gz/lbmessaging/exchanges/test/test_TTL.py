import json
import logging
import sys
import time
import unittest

from lbmessaging.exchanges.test import get_test_connection

from lbmessaging.exchanges.Common import Sender, Receiver


class TestPriorityQueue(unittest.TestCase):

    def setUp(self):
        self._connection = get_test_connection()
        self._channel = self._connection.channel()

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def test_existing(self):

        exchange = "test_ttl"
        queue = "test_queue_ttl"

        s = Sender(exchange, channel=self._channel)
        r = Receiver(exchange, queue, channel=self._channel)

        # Consume messages left over from previous runs
        r.receive_messages()

        mylist = list(range(5))

        for i in mylist:
            s.send_message("test", json.dumps([i]), expiration=1000)

        receivedlist = []
        msg = r.receive_message()
        logging.warning(msg)
        while msg:
            o = json.loads(msg[0])
            receivedlist.append(o[0])
            msg = r.receive_message()

        logging.warning(receivedlist)
        self.assertEqual(len(mylist), len(receivedlist))

    def test_expired(self):

        exchange = "test_ttl"
        queue = "test_queue_ttl"

        s = Sender(exchange, channel=self._channel)
        r = Receiver(exchange, queue, channel=self._channel)

        # Consume messages left over from previous runs
        r.receive_messages()

        mylist = list(range(5))

        for i in mylist:
            s.send_message("test", json.dumps([i]), expiration=900)
        time.sleep(1)
        receivedlist = []
        msg = r.receive_message()
        logging.warning(msg)
        while msg:
            o = json.loads(msg[0])
            receivedlist.append(o[0])
            msg = r.receive_message()

        logging.warning(receivedlist)
        # Should not receive any messages since we waited for the messages
        # to expire
        self.assertEqual(0, len(receivedlist))


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
