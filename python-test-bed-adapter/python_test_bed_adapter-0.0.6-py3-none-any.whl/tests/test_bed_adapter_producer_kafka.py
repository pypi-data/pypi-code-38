import unittest
import sys
import json
import os
sys.path.append("..")
from test_bed_adapter.options.test_bed_options import TestBedOptions
from test_bed_adapter import TestBedAdapter

import logging
logging.basicConfig(level=logging.INFO)

class TestProducerWithAdapter(unittest.TestCase):
    def invoke_producer(self, use_ssl, **keywords):
        self.message_was_sent = False

        # If no options are provided we grab them from file
        if (not "test_bed_options" in keywords.keys()):
            if use_ssl:
                options_file = open("config_files_for_testing/test_bed_options_for_tests_producer_using_ssl.json", encoding="utf8")
            else:
                options_file = open("config_files_for_testing/test_bed_options_for_tests_producer.json", encoding="utf8")
            options = json.loads(options_file.read())
            options_file.close()

            test_bed_options = TestBedOptions(options)
        else:
            test_bed_options = keywords["test_bed_options"]

        test_bed_adapter = TestBedAdapter(test_bed_options)

        message_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    "examples\\sample_messages\\example_amber_alert.json")
        example_message_file = open(message_path, encoding="utf-8")
        message_json = json.loads(example_message_file.read())
        example_message_file.close()

        messages = [{"message": message_json}]

        test_bed_adapter.on_sent += self.message_sent_handler
        test_bed_adapter.initialize()
        test_bed_adapter.producer_managers["standard_cap"].send_messages(messages)

        self.assertTrue(self.message_was_sent)
        test_bed_adapter.stop()

    def test_producer_using_adapter(self):
        # We test the procucer without using ssl
        self.invoke_producer(False)

        # We test the procucer without using
        #self.invoke_producer(True)

    def message_sent_handler(self,json_message):
        logging.info("\n\nmessage sent\n\n")
        logging.info(json_message)
        self.message_was_sent = True


if __name__ == '__main__':
    unittest.main()
