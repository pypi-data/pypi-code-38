import logging
import sys
import time
import unittest

from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange
from lbmessaging.exchanges.Common import get_connection

from pika import exceptions

QUEUE_NAME = "test_cvmfs_actions_queue"
ERROR_QUEUE_NAME = "test_cvmfs_actions_queue_errors"

class TestTimeout(unittest.TestCase):

    def get_broker(self):
        self._connection = get_connection(vhost='/lhcb-test',
                                          heartbeat_interval=1,
                                          blocked_connection_timeout=5)
        self._channel = self._connection.channel()
        broker = CvmfsDevExchange(self._channel)
        return broker

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def test_connection_closed(self):
        """ Check what happens when the server closes the connection """
        command = "test_cmd"
        args = ["arg1", "arg2"]
        # purge the queue
        broker = self.get_broker()
        broker.receive_all(QUEUE_NAME)
        logging.info("Sending 2 messages")
        broker.send_command(command, args)
        broker.send_command(command, args)
        logging.info("receiving the 1st")
        tmp = broker.receive_command(QUEUE_NAME)
        self.assertEqual(command, tmp.body.command)
        self.assertEqual(args, tmp.body.arguments)
        logging.info("Now waiting 10 seconds,"
                     " which should cause the conenction to timeout")
        time.sleep(10)
        try:
            logging.info("receiving the 2nd")
            tmp = broker.receive_command(QUEUE_NAME)
        except exceptions.ConnectionClosed as cc:
            logging.info("Connection was closed, trying with a new one...")
            new_broker = self.get_broker()
            tmp = new_broker.receive_command(QUEUE_NAME)
            self.assertEqual(command, tmp.body.command)
            self.assertEqual(args, tmp.body.arguments)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
