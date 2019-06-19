import logging
import sys
import unittest

from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange, \
    CVMFSDEV_EXCHANGE
from lbmessaging.exchanges.test import get_test_connection

from lbmessaging.exchanges.Common import AdminHelper, Receiver

QUEUE_NAME = "test_cvmfs_actions_queue"
QUEUE_NAME_CHANGED = "test_cvmfs_actions_queue_changed"
NEW_EXCHANGE = "cvmfsdev.action_backup"


class TestCvmfsDevMsg(unittest.TestCase):

    def setUp(self):
        self._connection = get_test_connection()
        self._channel = self._connection.channel()

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def _update_priority(self, message):
        if 'test_cmd_5' in message[0]:
            message[2].priority = 30
            return (True, message)
        return (False, message)

    def test_display(self):
        """ Check whether a the admin helpers display correctly the messages
        """
        broker = CvmfsDevExchange(self._channel)
        broker.receive_all(QUEUE_NAME)

        command = "test_cmd_%s"
        args = ["arg1", "arg2"]
        expected_results = []
        for i in range(0, 10):
            broker.send_command(command % i, args)
            expected_results.append([
                command % i, 3, 10, None, command % i,
                "['arg1', 'arg2']"
            ])
        # Test simple display
        tools = AdminHelper(CVMFSDEV_EXCHANGE,
                            channel=self._channel)
        res = tools.list_messages_in_queue(QUEUE_NAME)
        results_without_time = []
        for r in res:
            results_without_time.append([
                r[0], r[1], r[2], r[3], r[5], r[6].replace('u\'', '\'')
            ])
            self.assertTrue(r[4] is not None)

        self.assertEqual(expected_results, results_without_time)

        # Verify if all the messages are still in queue
        res = broker.receive_all(QUEUE_NAME)
        self.assertEqual(len(res), 10)

    def test_message_change(self):
        """ Check whether a the admin helpers display correctly the messages
        """
        broker = CvmfsDevExchange(self._channel)
        broker.receive_all(QUEUE_NAME)

        command = "test_cmd_%s"
        args = ["arg1", "arg2"]
        expected_results = []
        expected_results.append([
            command % 5, 3, 30, None, command % 5,
            "['arg1', 'arg2']"
        ])
        counter = 9
        for i in range(0, 10):
            broker.send_command(command % i, args)
            if i == 5:
                continue
            counter -= 1
            expected_results.append([
                command % i, 3, 10, None, command % i,
                "['arg1', 'arg2']"
            ])
        # Test simple display
        tools = AdminHelper(CVMFSDEV_EXCHANGE,
                            channel=self._channel)
        tools.change_messages(QUEUE_NAME, self._update_priority)
        res = tools.list_messages_in_queue(QUEUE_NAME)
        results_without_time = []
        for r in res:
            results_without_time.append([
                r[0], r[1], r[2], r[3], r[5], r[6].replace('u\'', '\'')
            ])
            self.assertTrue(r[4] is not None)

        self.assertEqual(expected_results, results_without_time)

        # Verify if all the messages are still in queue
        res = broker.receive_all(QUEUE_NAME)
        self.assertEqual(len(res), 10)

    def test_exchange_change(self):
        """ Check whether a the admin helpers display correctly the messages
        """
        broker = CvmfsDevExchange(self._channel)
        broker.receive_all(QUEUE_NAME)

        new_broker = Receiver(NEW_EXCHANGE,
                              QUEUE_NAME_CHANGED, channel=self._channel)
        # Consume messages left over from previous runs
        new_broker.receive_messages()

        command = "test_cmd_%s"
        args = ["arg1", "arg2"]
        expected_results = []
        counter = 9
        for i in range(0, 10):
            broker.send_command(command % i, args)
            if i == 5:
                continue
            counter -= 1
            expected_results.append([
                command % i, 3, 10, None, command % i,
                "['arg1', 'arg2']"
            ])
        # Test simple display
        tools = AdminHelper(CVMFSDEV_EXCHANGE,
                            channel=self._channel)
        tools.change_messages(QUEUE_NAME, self._update_priority,
                              dest_exchange=NEW_EXCHANGE)
        res = tools.list_messages_in_queue(QUEUE_NAME)
        results_without_time = []
        for r in res:
            results_without_time.append([
                r[0], r[1], r[2], r[3], r[5], r[6].replace('u\'', '\'')
            ])
            self.assertTrue(r[4] is not None)

        self.assertEqual(expected_results, results_without_time)

        # Verify if the 5th message is in the other exchange
        msgs = new_broker.receive_messages()
        self.assertEqual(len(msgs), 1)
        self.assertEqual(str(msgs[0][0][0]), "test_cmd_5")
        # Verify if all the messages are still in queue
        res = broker.receive_all(QUEUE_NAME)
        self.assertEqual(len(res), 9)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
