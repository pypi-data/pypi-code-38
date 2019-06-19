import logging
import multiprocessing
import signal
import sys
import unittest
from time import sleep

import os
from lbmessaging.exchanges.test import get_test_connection

from lbmessaging.exchanges.Common import Sender, Receiver, InterruptedProcessing

EXCHANGE = "test_exchange_signal"
QUEUE = "test_queue_signal"


def run_consumer(time_delay):
    logging.warning("Starting consume")
    connection = get_test_connection()

    r = Receiver(EXCHANGE, QUEUE, connection=connection)

    # Added signal handler
    def signal_handler(sig, frame):
        logging.warning("Received signal %s" % s)
        if sig in [ signal.SIGTERM,  signal.SIGINT ]:
            raise InterruptedProcessing("Controlled stop: %s" % sig)
        else:
            raise Exception("Uncontrolled stop: %s" % sig)

    for s in [ signal.SIGTERM, signal.SIGINT ]:
        signal.signal(s, signal_handler)

    # Now receiving...
    receivedlist = []
    def myconsumer(message):
        logging.warning("Processing:" + str(message.body))
        # Make sure we still sleep when the other process interrupts us...
        sleep(time_delay)
        receivedlist.append(message.body)
        return True

    try:
        msgs = r.consume_message(myconsumer)
    except:
        logging.warning("After consuming message")
        logging.debug(receivedlist)

class TestSignal(unittest.TestCase):


    def setUp(self):
        self._connection = get_test_connection()

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def test_signal_stop(self):

        # Consume messages left over from previous runs
        r = Receiver(EXCHANGE, QUEUE, connection=self._connection)
        r.receive_messages()

        # Now enqueuing
        logging.warning("Sending message to test server stop")
        txt = "LONG_RUNNING_TEST"
        self.send(txt)

        # Starting a child that will consume the messages
        time_delay = 10000
        logging.warning("Starting consumer process")
        p = multiprocessing.Process(target=run_consumer, args=([ time_delay ]))
        p.start()
        sleep(1)

        # sending SIGTERM to child
        os.kill(p.pid, signal.SIGTERM)

        # Waiting for child to finish
        p.join()
        self.assertEqual(0, p.exitcode)

        # The message should still be in the queue !
        m = r.receive_message()
        self.assertIsNotNone(m)
        self.assertEqual(txt, m.body)

    def test_signal_crash(self):

        # Consume messages left over from previous runs
        r = Receiver(EXCHANGE, QUEUE, connection=self._connection)
        r.receive_messages()

        # Now enqueuing
        logging.warning("Sending message to test crash")
        txt = "LONG_RUNNING_TEST"
        self.send(txt)

        # Starting a child that will consume the messages
        time_delay = 10000
        logging.warning("Starting consumer process")
        p = multiprocessing.Process(target=run_consumer, args=([ time_delay ]))
        p.start()
        sleep(1)

        # sending SIGABRT to child
        os.kill(p.pid, signal.SIGABRT)

        # Waiting for child to finish
        p.join()
        self.assertNotEquals(0, p.exitcode)

        # The message should still be in the queue !
        m = r.receive_message()
        self.assertIsNotNone(m)
        self.assertEqual(txt, m.body)


    def send(self, message_text):
        s = Sender(EXCHANGE, connection=self._connection)
        s.send_message("test", message_text)



if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
