import logging
import unittest
import datetime
import json
from tests.test_bed_adapter_producer_kafka import TestProducerWithAdapter
from test_bed_adapter.options.test_bed_options import TestBedOptions

import sys
sys.path.append("..")


logging.basicConfig(level=logging.INFO)


class TestConsumerChangingId(unittest.TestCase):
    @unittest.skip("Uncomplete test. Needs work")
    def test_consumer_changing_id(self):

        self.send_initial_message()

        options_file_consumer = open("config_files_for_testing/test_bed_options_for_tests_consumer_changing_id.json", encoding="utf8")
        options_producer = json.loads(options_file_consumer.read())
        options_file_consumer.close()

        test_bed_options_for_consumer = TestBedOptions(options_producer)

        # test_bed_options_for_consumer.client_id = test_bed_options_for_consumer.client_id + "---" + str(datetime.datetime.now())

    @unittest.skip("Uncomplete test. Needs work")
    def send_initial_message(self):
        options_file_producer = open("config_files_for_testing/test_bed_options_for_tests_producer.json",
                                     encoding="utf8")
        options_producer = json.loads(options_file_producer.read())
        options_file_producer.close()

        test_bed_options_for_producer = TestBedOptions(options_producer)
        test_bed_options_for_producer.client_id = test_bed_options_for_producer.client_id + "---" + str(
            datetime.datetime.now())

        unittest_producer = TestProducerWithAdapter()
        unittest_producer.invoke_producer(use_ssl=False, test_bed_options=test_bed_options_for_producer)

if __name__ == '__main__':
    unittest.main()
