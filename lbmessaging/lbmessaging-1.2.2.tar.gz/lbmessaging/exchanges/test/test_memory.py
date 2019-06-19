import logging
import sys
import unittest

from lbmessaging.exchanges.test import get_test_connection

from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange

QUEUE_NAME = "test_memory"

class TestMemory(unittest.TestCase):

    def setUp(self):
        self._connection = get_test_connection()
        self._channel = self._connection.channel()

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def test_simple(self):
        """ Check whether a simple command gets through """
        command = "test_cmd"
        args = ["arg1", "arg2"]
        broker = CvmfsDevExchange(self._channel)
        broker.send_command(command, args)
        tmp = broker.receive_command(QUEUE_NAME)
        self.assertEqual(command, tmp.body.command)
        self.assertEqual(args, tmp.body.arguments)

    def test_send_many_messages(self):
        """ Check that we do not use too many resources when sending many messages"""
        command = "test_cmd"
        args = ["arg1", "arg2"]
        broker = CvmfsDevExchange(self._channel)
        broker.receive_all(QUEUE_NAME) # Purge all messages
        for i in range(1000):
            mycmd = command + "_%d" % i
            broker.send_command(mycmd, args)
            tmp = broker.receive_command(QUEUE_NAME)
            self.assertEqual(mycmd, tmp.body.command)
            self.assertEqual(args, tmp.body.arguments)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
