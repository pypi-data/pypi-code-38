import logging
import sys
import unittest

from lbmessaging.exchanges.PeriodicTestsExchange import PeriodicTestsExchange
from lbmessaging.exchanges.test import get_test_connection


QUEUE_NAME = "test_pr_test_queue"


class TestCvmfsDevMsg(unittest.TestCase):

    def setUp(self):
        self._connection = get_test_connection()
        self._channel = self._connection.channel()

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def test_simple(self):
        """ Check whether a simple command gets through """
        slot = 'slot1'
        build_id = 'buildId1'
        project = 'project1'
        platform = 'platform1'
        group = 'group1'
        env = 'env1'
        runner = 'runner1'
        os_label = 'os_label1'
        broker = PeriodicTestsExchange(self._channel)
        # purge the queue
        broker.get_tests_to_run(QUEUE_NAME)

        broker.request_test(slot, build_id, project,
                            platform, group, env, runner, os_label)
        tmp = broker.get_test_to_run(QUEUE_NAME)
        self.assertEqual(slot, tmp.body.slot)
        self.assertEqual(build_id, tmp.body.build_id)
        self.assertEqual(project, tmp.body.project)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(group, tmp.body.group)
        self.assertEqual(env, tmp.body.env)
        self.assertEqual(runner, tmp.body.runner)
        self.assertEqual(os_label, tmp.body.os_label)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
