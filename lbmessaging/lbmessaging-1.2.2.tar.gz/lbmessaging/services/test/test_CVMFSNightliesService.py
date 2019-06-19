import logging
import sys
import unittest

from lbmessaging.services.CVMFSNightliesService import CVMFSNightliesService
from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange
from lbmessaging.exchanges.test import get_test_connection


QUEUE_NAME = "test_cvmfs_actions_queue"


class TestCVMFSNightliesService(unittest.TestCase):

    def setUp(self):
        channel = get_test_connection().channel()
        broker = CvmfsDevExchange(channel)
        broker.receive_all(QUEUE_NAME)

    def tearDown(self):
        pass

    def test_services(self):
        command = "test_cmd"
        args = ["arg1", "arg2"]
        srv = CVMFSNightliesService(vhost='/lhcb-test')
        srv.dev_send(command, args)
        tmp = srv.dev_receive(QUEUE_NAME)
        self.assertEqual(command, tmp.body.command)
        self.assertEqual(args, tmp.body.arguments)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
