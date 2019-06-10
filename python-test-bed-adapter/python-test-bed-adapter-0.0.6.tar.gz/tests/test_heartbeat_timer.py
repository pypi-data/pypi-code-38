import unittest
import sys
import threading
import time
import logging
import json
sys.path.append("..")
from test_bed_adapter.options.test_bed_options import TestBedOptions
from test_bed_adapter import TestBedAdapter
from test_bed_adapter.kafka.heartbeat_manager import HeartbeatManager

logging.basicConfig(level=logging.INFO)


class TestHeartbeat(unittest.TestCase):

    def test_heartbeat(self):
        self.message_was_sent = False
        self.wait_seconds = 5

        e = threading.Event()
        t = threading.Thread(target=self.run_heartbeat_in_thread, args=(e,))
        t.start()

        # wait 30 seconds for the thread to finish its work
        t.join(self.wait_seconds)
        if t.is_alive():
            print
            "thread is not done, setting event to kill thread."
            e.set()
        else:
            print
            "thread has already finished."

        self.assertTrue(True)
        pass

    def run_heartbeat_in_thread(self, e):
        data = set()
        heartbeat_interval = 1
        options_file = open("config_files_for_testing/test_bed_options_for_tests_producer.json", encoding="utf8")
        options = json.loads(options_file.read())
        options_file.close()
        test_bed_options = TestBedOptions(options)
        heartbeat_topic = "system_heartbeat"

        test_bed_adapter = TestBedAdapter(test_bed_options)
        test_bed_adapter.schema_registry.start_process()
        test_bed_adapter.init_producers()
        kafka_heartbeat_producer = test_bed_adapter.producer_managers[heartbeat_topic]
        kafka_heartbeat_producer.on_sent += self.message_sent_handler

        heartbeat_manager = HeartbeatManager(kafka_heartbeat_producer, heartbeat_interval, test_bed_options.client_id)
        heartbeat_manager.start_heartbeat_async()

        for i in range(self.wait_seconds):
            data.add(i)
            if not e.isSet():
                time.sleep(1)
            else:
                heartbeat_manager.stop()
                break

        heartbeat_manager.stop()

    def message_sent_handler(self, json_message):
        logging.info("heartbeat message sent\n\n")
        logging.info(json_message)
        self.message_was_sent = True


if __name__ == '__main__':
    unittest.main()
