import json
import logging
import random
import sys
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

    def test_order(self):

        exchange = "test_exchange"
        queue = "test_queue"

        s = Sender(exchange, channel=self._channel)
        r = Receiver(exchange, queue, channel=self._channel)

        # Consume messages left over from previous runs
        r.receive_messages()

        mylist = list(range(5))
        random.shuffle(mylist)

        for i in mylist:
            s.send_message("test", json.dumps([i]), priority=i)

        receivedlist = []
        msg = r.receive_message()
        logging.debug(msg)
        while msg:
            o = json.loads(msg[0])
            receivedlist.append(o[0])
            msg = r.receive_message()

        logging.debug(receivedlist)
        # Checking that we have the same number of messages and
        # that they are sorted correctly...
        self.assertEqual(len(mylist), len(receivedlist))
        self.assertEqual(sorted(receivedlist)[::-1], receivedlist)

    def test_order_bulk(self):

        exchange = "test_exchange"
        queue = "test_queue"

        s = Sender(exchange, channel=self._channel)
        r = Receiver(exchange, queue, channel=self._channel)

        # Consume messages left over from previous runs
        r.receive_messages()

        mylist = list(range(5))
        random.shuffle(mylist)

        for i in mylist:
            s.send_message("test", json.dumps([i]), priority=i)

        receivedlist = []
        msgs = r.receive_messages()
        for msg in msgs:
            o = json.loads(msg[0])
            receivedlist.append(o[0])
            msg = r.receive_message()

        logging.debug(receivedlist)
        # Checking that we have the same number of messages and that
        # they are sorted correctly...
        self.assertEqual(len(mylist), len(receivedlist))
        self.assertEqual(sorted(receivedlist)[::-1], receivedlist)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
