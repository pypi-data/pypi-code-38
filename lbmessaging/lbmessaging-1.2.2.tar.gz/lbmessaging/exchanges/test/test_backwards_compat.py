import logging
import sys
import unittest

from lbmessaging.exchanges.test import get_test_connection

from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange

QUEUE_NAME = "test_backwards_compat"

class TestMemory(unittest.TestCase):

    def setUp(self):
        self._connection = get_test_connection()

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def test_connection(self):
        """ Pass a connection instead of a channel to the API """
        command = "test_connection"
        args = ["arg1", "arg2"]
        broker = CvmfsDevExchange(self._connection)
        broker.receive_all(QUEUE_NAME) # Purge of old messages
        broker.send_command(command, args)
        tmp = broker.receive_command(QUEUE_NAME)
        self.assertEqual(command, tmp.body.command)
        self.assertEqual(args, tmp.body.arguments)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
