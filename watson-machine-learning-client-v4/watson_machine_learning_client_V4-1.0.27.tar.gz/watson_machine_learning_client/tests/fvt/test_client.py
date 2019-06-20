import unittest
import os
from configparser import ConfigParser
import json
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.wml_client_error import *


if "ENV" in os.environ:
    environment = os.environ['ENV']
else:
    environment = "FVT"


class TestClient(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    scoring_uid = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestClient.logger.info("Service Instance: setting up credentials")
        config = ConfigParser()
        config.read('../config.ini')
        self.wml_credentials = json.loads(config.get(environment, 'wml_credentials'))
        print(self.wml_credentials)
        self.wml_credentials_invalid = self.wml_credentials.copy()
        self.wml_credentials_invalid['username'] = "11111111-2222-4308-2222-d50725164a9d"

        self.wml_lib = __import__('watson_machine_learning_client', globals(), locals())

    def test_01_create_wml_client(self):
        self.client = self.wml_lib.WatsonMachineLearningAPIClient(wml_credentials=self.wml_credentials)
        self.assertIsNotNone(self.client)

    def test_01_create_wml_client_empty_credentials(self):
        with self.assertRaises(WMLClientError):
            self.wml_lib.WatsonMachineLearningAPIClient(wml_credentials="")

    def test_01_create_wml_client_empty_json_credentials(self):
        with self.assertRaises(WMLClientError):
            self.wml_lib.WatsonMachineLearningAPIClient(wml_credentials="")

    def test_01_create_wml_client_no_credentials(self):
        with self.assertRaises(TypeError):
            self.wml_lib.WatsonMachineLearningAPIClient()

    def test_01_create_wml_client_invalid_credentials(self):
        with self.assertRaises(WMLClientError) as context:
            self.wml_lib.WatsonMachineLearningAPIClient(wml_credentials=self.wml_credentials_invalid)
        self.assertIn("Invalid credentials", str(context.exception))


if __name__ == '__main__':
    unittest.main()
