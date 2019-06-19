import logging
import sys
import unittest

from lbmessaging.exchanges.CommandExchange import command_retry_count
from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange
from lbmessaging.exchanges.CvmfsProdExchange import CvmfsProdExchange
from lbmessaging.exchanges.test import get_test_connection

from lbmessaging.exchanges.CvmfsConDBExchange import CvmfsConDBExchange

QUEUE_NAME = "test_cvmfs_actions_queue"


class TestCvmfsDevMsg(unittest.TestCase):

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
        # purge the queue
        broker.receive_all(QUEUE_NAME)

        broker.send_command(command, args)
        tmp = broker.receive_command(QUEUE_NAME)
        self.assertEqual(command, tmp.body.command)
        self.assertEqual(args, tmp.body.arguments)

    def test_condb(self):
        """ Check whether the cvmfs cond exchange works """
        command = "test_cmd"
        args = ["arg1", "arg2"]
        broker = CvmfsConDBExchange(self._channel)
        # purge queue first
        broker.receive_all("test_cvmfscondb_actions_queue")
        broker.send_command(command, args)
        tmp = broker.receive_command("test_cvmfscondb_actions_queue")
        self.assertEqual(command, tmp.body.command)
        self.assertEqual(args, tmp.body.arguments)

    def test_prod(self):
        """ Check the cvmfs prod exchange works """
        command = "test_cmd"
        args = ["arg1", "arg2"]
        broker = CvmfsProdExchange(self._channel)
        # purge queue first
        broker.receive_all("test_cvmfsprod_actions_queue")
        broker.send_command(command, args)
        tmp = broker.receive_command("test_cvmfsprod_actions_queue")

        self.assertEqual(command, tmp.body.command)
        self.assertEqual(args, tmp.body.arguments)

    def test_priority(self):
        """ Check the priority system """
        broker = CvmfsDevExchange(self._channel)

        # purge the queue
        broker.receive_all(QUEUE_NAME)

        # Now adding our commands
        cmds_low = ["low1", "low2", "low3"]
        cmd_high = "high1"
        for cmd in cmds_low:
            broker.send_command(cmd, [], 2)

        # Make sure we get the first command
        tmp = broker.receive_command(QUEUE_NAME)
        self.assertEqual(cmds_low[0], tmp.body.command)

        # Now enqueue a high priority command and check it's coming
        # before the others
        broker.send_command(cmd_high, [], 100)
        tmp = broker.receive_command(QUEUE_NAME)
        self.assertEqual(cmd_high, tmp.body.command)

        # Now check that we have the others too
        tmp = broker.receive_command(QUEUE_NAME)
        self.assertEqual(cmds_low[1], tmp.body.command)

        tmp = broker.receive_command(QUEUE_NAME)
        self.assertEqual(cmds_low[2], tmp.body.command)

    def test_error(self):
        """ Check the priority system """
        broker = CvmfsDevExchange(self._channel)

        # purge the queue
        broker.receive_all(QUEUE_NAME)
        broker.receive_command_error_all(QUEUE_NAME)

        # Now adding our command
        cmd = "test_command"
        broker.send_command(cmd, [], 100, max_retry=1)
        tmp = broker.receive_command(QUEUE_NAME)
        self.assertEqual(cmd, tmp.body.command)

        # Pretend we have a processing error
        broker.handle_processing_error(tmp, queue_name=QUEUE_NAME)
        tmp2 = broker.receive_command(QUEUE_NAME)
        self.assertEqual(0, command_retry_count(tmp2))

        # Pretend we have a processing error again
        broker.handle_processing_error(tmp2, queue_name=QUEUE_NAME)
        tmp3 = broker.receive_command_error(QUEUE_NAME)
        self.assertEqual(cmd, tmp3.body.command)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
