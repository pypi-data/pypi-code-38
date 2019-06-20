import unittest
import os
from configparser import ConfigParser
import json
from importlib import reload
import site
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.wml_client_error import *


if "ENV" in os.environ:
    environment = os.environ['ENV']
else:
    environment = "SVT"


class TestTraining(unittest.TestCase):
    training_configuration_dict = None
    definition_url = None
    definition_uid = None
    training_details_uid = None
    training_details_url = None
    trained_model_url = None
    trained_model_uid = None

    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        config = ConfigParser()
        config.read('../config.ini')
        self.wml_credentials = json.loads(config.get(environment, 'wml_credentials'))
        self.wml_lib = __import__('watson_machine_learning_client', globals(), locals())
        self.client = self.wml_lib.WatsonMachineLearningAPIClient(self.wml_credentials)

        metadata = {
            self.client.repository.DefinitionMetaNames.NAME: "my_training_definition",
            self.client.repository.DefinitionMetaNames.DESCRIPTION: "my_description",
            self.client.repository.DefinitionMetaNames.AUTHOR_NAME: "John Smith",
            self.client.repository.DefinitionMetaNames.AUTHOR_EMAIL: "js@js.com",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: "1.5",
            self.client.repository.DefinitionMetaNames.RUNTIME_NAME: "python",
            self.client.repository.DefinitionMetaNames.RUNTIME_VERSION: "3.5",
            self.client.repository.DefinitionMetaNames.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20"
        }

        model_content_path = './artifacts/tf-softmax-model.zip'
        definition_details = self.client.repository.store_definition(training_definition=model_content_path, meta_props=metadata)

        TestTraining.definition_url = self.client.repository.get_definition_url(definition_details)
        TestTraining.definition_uid = self.client.repository.get_definition_uid(definition_details)

        TestTraining.logger.info("Saved model definition url: " + str(TestTraining.definition_url))
        TestTraining.logger.info("Saved model definition uid: " + str(TestTraining.definition_uid))

    def test_00_test_configuration_metanames(self):
        TestTraining.training_configuration_dict = {
            self.client.training.ConfigurationMetaNames.NAME: "Hand-written Digit Recognition",
            self.client.training.ConfigurationMetaNames.AUTHOR_NAME: "John Smith",
            self.client.training.ConfigurationMetaNames.AUTHOR_EMAIL: "JohnSmith@js.com",
            self.client.training.ConfigurationMetaNames.DESCRIPTION: "Hand-written Digit Recognition training",
            self.client.training.ConfigurationMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.client.training.ConfigurationMetaNames.FRAMEWORK_VERSION: "1.5-py3",
            self.client.training.ConfigurationMetaNames.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20",
            self.client.training.ConfigurationMetaNames.EXECUTION_RESOURCE_SIZE: 'k80',
            self.client.training.ConfigurationMetaNames.TRAINING_DATA_REFERENCE: {
                "connection": {
                    "auth_url": "https://s3-api.us-geo.objectstorage.service.networklayer.com",
                    "userId": "zfho4HT7pUIStZvSkDsl",
                    "password": "21q66Vvxkhr4uPDacTf8F9fnzMjSUIzsZRtxrYbx"
                },
                "source": {
                    "bucket": "wml-dev",
                },
                "type": "s3"
            },
            self.client.training.ConfigurationMetaNames.TRAINING_RESULTS_REFERENCE: {
                "connection": {
                    "auth_url": "https://s3-api.us-geo.objectstorage.service.networklayer.com",
                    "userId": "zfho4HT7pUIStZvSkDsl",
                    "password": "21q66Vvxkhr4uPDacTf8F9fnzMjSUIzsZRtxrYbx"
                },
                "target": {
                    "bucket": "wml-dev-results",
                },
                "type": "s3"
            },
        }

    def test_01_run_training_url(self):
        TestTraining.training_details_url = self.client.training.run(definition_url=TestTraining.definition_url, meta_props=TestTraining.training_configuration_dict, asynchronous=False)
        self.assertIn('training', str(TestTraining.training_details_url))

    def test_01_run_training_uid(self):
        TestTraining.training_details_uid = self.client.training.run(definition_uid=TestTraining.definition_uid, meta_props=TestTraining.training_configuration_dict, asynchronous=False)
        self.assertIn('training', str(TestTraining.training_details_uid))

    def test_01_run_training_no_definition(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.training.run(meta_props=TestTraining.training_configuration_dict, asynchronous=False)
        self.assertIn("Both uid and url are empty.", str(context.exception))

    def test_01_run_training_none_url_definition(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.training.run(definition_url=None, meta_props=TestTraining.training_configuration_dict, asynchronous=False)
        self.assertIn("Both uid and url are empty.", str(context.exception))

    def test_01_run_training_none_uid_definition(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.training.run(definition_uid=None, meta_props=TestTraining.training_configuration_dict, asynchronous=False)
        self.assertIn("Both uid and url are empty.", str(context.exception))

    def test_01_run_training_empty_url_definition(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.training.run(definition_url="", meta_props=TestTraining.training_configuration_dict, asynchronous=False)
        self.assertIn("Passed url is not valid", str(context.exception))

    def test_01_run_training_empty_uid_definition(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.training.run(definition_uid="", meta_props=TestTraining.training_configuration_dict, asynchronous=False)
        self.assertIn("Invalid uid", str(context.exception))

    def test_01_run_training_invalid_url_definition(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.training.run(definition_url="https://ibm-watson-ml.mybluemix.net", meta_props=TestTraining.training_configuration_dict, asynchronous=False)
        self.assertIn("Passed url is not valid", str(context.exception))

    def test_01_run_training_invalid_uid_definition(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.training.run(definition_uid="dsakkf7djfdnsnf", meta_props=TestTraining.training_configuration_dict, asynchronous=False)
        self.assertIn("Invalid uid", str(context.exception))

    def test_02_get_run_uid(self):
        TestTraining.trained_model_uid = self.client.training.get_run_uid(run_details=TestTraining.training_details_uid)
        self.assertIn('training', str(TestTraining.trained_model_uid))

    def test_03_get_run_url(self):
        TestTraining.trained_model_url = self.client.training.get_run_url(run_details=TestTraining.training_details_url)
        self.assertIn('training', str(TestTraining.trained_model_url))

    def test_04_get_status_uid(self):
        status = self.client.training.get_status(run_uid=TestTraining.trained_model_uid)
        self.assertIn('state', status)

    def test_04_get_status_url(self):
        status = self.client.training.get_status(run_url=TestTraining.trained_model_url)
        self.assertIn('state', status)

    def test_05_get_details_uid(self):
        details = self.client.training.get_details(run_uid=TestTraining.trained_model_uid)

        self.assertIn('entity', str(details))
        self.assertIn('status', str(details))
        self.assertIn('state', str(details))

    def test_05_get_details_url(self):
        details = self.client.training.get_details(run_url=TestTraining.trained_model_url)

        self.assertIn('entity', str(details))
        self.assertIn('status', str(details))
        self.assertIn('state', str(details))

    def test_06_list_trained_models(self):
        self.client.training.list()

    def test_07_monitor(self):
        pass

    def test_08_cancel(self):
        pass

    def test_09_delete_training_uid(self):
        self.client.training.delete(run_uid=TestTraining.trained_model_uid)
        self.assertTrue(str(TestTraining.trained_model_uid) not in str(self.client.training.get_details()))

    def test_09_delete_training_url(self):
        self.client.training.delete(run_url=TestTraining.trained_model_url)
        self.assertTrue(str(TestTraining.trained_model_url) not in str(self.client.training.get_details()))

