import logging
import sys
import threading
import time
import unittest

from lbmessaging.exchanges.test import get_test_connection

from lbmessaging.exchanges.Common import RPCServer, RPCClient

QUEUE_NAME = "test_rpc"
EXCHANGE_NAME = 'cvmfs.test.rpc'


class TestRPC(unittest.TestCase):

    def setUp(self):
        self._connection = get_test_connection()
        self._connection_server = get_test_connection()
        self._channel = self._connection.channel()
        self._channel_server = self._connection_server.channel()

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def _trigger_server(self):
        server = RPCServer(EXCHANGE_NAME, QUEUE_NAME,
                           channel=self._channel_server,
                           auto_delete=True)

        def wrapper(message):
            self.assertEqual(message.body['question'], 'Done?')
            return {'result': 'Done'}

        server.receive_and_replay_rpc_message(wrapper, limit=1)

    def test_rpc(self):
        """ Check whether a simple command gets through """
        server_thread = threading.Thread(target=self._trigger_server)
        server_thread.start()
        time.sleep(1)
        client = RPCClient(EXCHANGE_NAME,
                           routing_keys=None,
                           auto_delete=True,
                           channel=self._channel)

        def wrapper(message):
            self.assertEqual(message.body['result'], 'Done')
            return True

        client.send_and_receive_rpc_message(QUEUE_NAME,
                                            {'question': 'Done?'},
                                            wrapper, limit=1)
        server_thread.join()

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
