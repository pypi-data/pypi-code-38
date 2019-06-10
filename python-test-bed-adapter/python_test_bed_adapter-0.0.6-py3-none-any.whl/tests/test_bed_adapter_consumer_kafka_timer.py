import unittest
import sys
import threading
import time
import logging
import json
sys.path.append("..")
import datetime
from test_bed_adapter.options.test_bed_options import TestBedOptions
from test_bed_adapter import TestBedAdapter
logging.basicConfig(level=logging.INFO)

class TestConsumerWithAdapter(unittest.TestCase):

    def test_consumer_from_adapter(self, **keywords):
        self.was_any_message_obtained = False
        self.wait_seconds = 5

        #If no options are provided we grab them from file
        if (not "test_bed_options" in keywords.keys()):
            options_file = open("config_files_for_testing/test_bed_options_for_tests_consumer.json", encoding="utf8")
            options = json.loads(options_file.read())
            options_file.close()

            test_bed_options = TestBedOptions(options)
            test_bed_options.client_id = test_bed_options.client_id + "---" + str(datetime.datetime.now())
            test_bed_adapter = TestBedAdapter(test_bed_options)
        else:
            test_bed_options = keywords["test_bed_options"]

        #We add the message handler
        test_bed_adapter.on_message += self.handle_message

        e = threading.Event()
        t = threading.Thread(target=self.run_consumer_in_thread, args=(e, test_bed_adapter))
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

        # If we have a parameter with a boolean "expect_messages" we check that we obtained messages according to it.
        if ("expect_messages" in keywords.keys()):
            self.assertTrue(keywords["expect_messages"] == self.was_any_message_obtained)
        else:
            self.assertTrue(self.was_any_message_obtained)

        test_bed_adapter.stop()
        pass

    def handle_message(self,message):
        logging.info("\n\n-------\n\n")
        self.was_any_message_obtained=True
        logging.info(message)

    def run_consumer_in_thread(self, e, test_bed_adapter):
        data = set()
        test_bed_adapter.initialize()
        test_bed_adapter.consumer_managers["standard_cap"].listen_messages()
        # test_bed_adapter.consumers["simulation-entity-item"].listen_messages()

        for i in range(self.wait_seconds):
            data.add(i)
            if not e.isSet():
                time.sleep(1)
            else:
                break

if __name__ == '__main__':
    unittest.main()
