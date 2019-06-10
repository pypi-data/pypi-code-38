import unittest
import sys
import json
sys.path.append("..")
from test_bed_adapter.options.test_bed_options import TestBedOptions
from test_bed_adapter import TestBedAdapter

import logging
logging.basicConfig(level=logging.INFO)

class TestConsumerWithAdapter(unittest.TestCase):
    @unittest.skip("Skip this test if you are going to run many tests, because this could block the stack")
    def test_consumer_using_adapter(self):
        self.was_any_message_obtained = False

        options_file = open("config_files_for_testing/test_bed_options_for_tests_consumer.json", encoding="utf8")
        options = json.loads(options_file.read())
        options_file.close()

        test_bed_options = TestBedOptions(options)
        test_bed_adapter = TestBedAdapter(test_bed_options)

        # We add the message handler
        test_bed_adapter.on_sent += self.handle_message

        test_bed_adapter.initialize()
        topic=list(test_bed_adapter.consumer_managers.keys())[0]
        test_bed_adapter.consumer_managers[topic].listen_messages()

        self.assertEqual(True, True)
        test_bed_adapter.stop()

    def handle_message(self,message):
        logging.info("-------")
        self.was_any_message_obtained=True
        logging.info(message)


if __name__ == '__main__':
    unittest.main()
