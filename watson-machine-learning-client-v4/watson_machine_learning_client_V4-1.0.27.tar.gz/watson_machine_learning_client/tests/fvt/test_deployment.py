
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
    environment = "FVT"


class TestDeployment(unittest.TestCase):
    deployment_uid = None
    deployment_uid_2 = None
    deployment_url = None
    deployment_url_2 = None
    deployment_details = None
    model_uid = "a29e6f0e-20eb-4a03-8e1a-9dad86bc1cc0"
    model_url = "https://ibm-watson-ml-fvt.stage1.mybluemix.net/v3/wml_instances/3269d065-4881-4f88-bb66-4416f95ba3de/published_models/a29e6f0e-20eb-4a03-8e1a-9dad86bc1cc0"
    scoring_url = None
    scoring_uid = None

    scoring_data = {'values': [
        [0.0, 0.0, 5.0, 16.0, 16.0, 3.0, 0.0, 0.0, 0.0, 0.0, 9.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 2.0,
         0.0, 0.0, 0.0, 0.0, 1.0, 15.0, 16.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 9.0, 13.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0,
         0.0, 0.0, 14.0, 12.0, 0.0, 0.0, 0.0, 0.0, 5.0, 12.0, 16.0, 8.0, 0.0, 0.0, 0.0, 0.0, 3.0, 15.0, 15.0, 1.0, 0.0,
         0.0],
        [0.0, 0.0, 6.0, 16.0, 12.0, 1.0, 0.0, 0.0, 0.0, 0.0, 5.0, 16.0, 13.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 5.0,
         15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 13.0, 0.0, 0.0, 0.0, 0.0,
         0.0, 6.0, 16.0, 9.0, 4.0, 1.0, 0.0, 0.0, 3.0, 16.0, 16.0, 16.0, 16.0, 10.0, 0.0, 0.0, 5.0, 16.0, 11.0, 9.0,
         6.0, 2.0]]}

    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestDeployment.logger.info("Service Instance: setting up credentials")
        config = ConfigParser()
        config.read('../config.ini')
        self.wml_credentials = json.loads(config.get(environment, 'wml_credentials'))
        self.wml_lib = __import__('watson_machine_learning_client', globals(), locals())
        self.client = self.wml_lib.WatsonMachineLearningAPIClient(self.wml_credentials)

    def test_01_create_deployment_uid(self):
        TestDeployment.deployment_details = self.client.deployments.create(artifact_uid=self.model_uid, name="Deployment test PLP")
        self.assertIsNotNone(self.deployment_details)
        self.assertIsNotNone(self.deployment_details['entity'])
        self.assertIsNotNone(self.deployment_details['metadata'])
        self.assertIsNotNone(self.deployment_details['entity']['scoring_url'])

        TestDeployment.scoring_url = self.deployment_details['entity']['scoring_url']
        TestDeployment.deployment_uid = self.deployment_details['metadata']['guid']
        TestDeployment.deployment_url = self.deployment_details['metadata']['url']

    def test_01_create_deployment_url(self):
        deployment_details = self.client.deployments.create(model_url=self.model_url, name="Deployment 2 test PLP")
        self.assertIsNotNone(deployment_details)
        self.assertIsNotNone(deployment_details['entity'])
        self.assertIsNotNone(deployment_details['metadata'])
        self.assertIsNotNone(deployment_details['entity']['scoring_url'])

        TestDeployment.scoring_url_2 = deployment_details['entity']['scoring_url']
        TestDeployment.deployment_url_2 = deployment_details['metadata']['url']
        TestDeployment.deployment_uid_2 = deployment_details['metadata']['guid']

    def test_01_create_deployment_invalid_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.create(artifact_uid="sadrjfdjsf899ssksksss", name="Deployment test PLP")

        self.assertIn("Invalid uid", str(context.exception))

    def test_01_create_deployment_empty_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.create(artifact_uid="", name="Deployment test PLP")

        self.assertIn("Invalid uid", str(context.exception))

    def test_01_create_deployment_json_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.create(artifact_uid="{}", name="Deployment test PLP")

        self.assertIn("Invalid uid", str(context.exception))

    def test_01_create_deployment_empty_name(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.create(artifact_uid=self.model_uid, name="")

        self.assertIn("Invalid", str(context.exception))

    def test_01_create_deployment_none_name(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.create(artifact_uid=self.model_uid, name=None)

        self.assertIn("Invalid", str(context.exception))

    def test_01_create_deployment_no_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.create(name="Test PLP")

        self.assertIn("Both uid and url are empty", str(context.exception))

    def test_01_create_deployment_no_name(self):
        with self.assertRaises(TypeError):
            self.client.deployments.create(artifact_uid=self.model_uid)

    def test_02_get_deployment_uid(self):
        deployment_uid = self.client.deployments.get_deployment_uid(deployment_details=TestDeployment.deployment_details)
        self.assertEqual(deployment_uid, TestDeployment.deployment_uid)

    def test_02_get_deployment_uid_no_details(self):
        with self.assertRaises(TypeError):
            self.client.deployments.get_deployment_uid()

    def test_02_get_deployment_uid_none_details(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.get_deployment_uid(deployment_details=None)

    def test_02_get_deployment_uid_empty_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.get_deployment_uid(deployment_details="")

        self.assertIn("Invalid", str(context.exception))

    def test_02_get_deployment_uid_empty_json(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.get_deployment_uid(deployment_details="{}")

        self.assertIn("Invalid", str(context.exception))

    def test_03_get_scoring_url(self):
        scoring_url = self.client.deployments.get_scoring_url(deployment=TestDeployment.deployment_details)
        self.assertEqual(scoring_url, TestDeployment.scoring_url)

    def test_03_get_scoring_url_no_details(self):
        with self.assertRaises(TypeError):
            self.client.deployments.get_scoring_url()

    def test_03_get_scoring_url_none_details(self):
        with self.assertRaises(MissingValue):
            self.client.deployments.get_scoring_url(deployment=None)

    def test_03_get_scoring_url_empty_details(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.get_scoring_url(deployment="")

    def test_03_get_scoring_url_empty_json(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.get_scoring_url(deployment="{}")

    def test_04_get_details(self):
        details = self.client.deployments.get_details()
        self.assertIn(TestDeployment.deployment_url, str(details))

    def test_04_get_details_uid(self):
        details = self.client.deployments.get_details(deployment_uid=self.deployment_uid)
        self.assertIn(TestDeployment.deployment_url, str(details))

    def test_04_get_details_url(self):
        details = self.client.deployments.get_details(deployment_url=self.deployment_url)
        self.assertIn(TestDeployment.deployment_url, str(details))

    def test_04_get_details_url_and_uid(self):
        details = self.client.deployments.get_details(deployment_uid=self.deployment_uid, deployment_url=self.deployment_url)
        self.assertIn(TestDeployment.deployment_url, str(details))

    def test_04_get_details_none_url(self):
        details = self.client.deployments.get_details(deployment_url=None)
        self.assertIn("resources", str(details))
        self.assertIn(TestDeployment.deployment_url, str(details))

    def test_04_get_details_none_uid(self):
        details = self.client.deployments.get_details(deployment_uid=None)
        self.assertIn("resources", str(details))
        self.assertIn(TestDeployment.deployment_url, str(details))

    def test_04_get_details_empty_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.get_details(deployment_url="")

        self.assertIn("is not an url", str(context.exception))

    def test_04_get_details_empty_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.get_details(deployment_uid="")

        self.assertIn("is not an uid", str(context.exception))

    def test_04_get_details_empty_json_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.get_details(deployment_url="{}")

        self.assertIn("is not an url", str(context.exception))

    def test_04_get_details_empty_json_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.get_details(deployment_uid="{}")

        self.assertIn("is not an uid", str(context.exception))

    def test_05_list(self):
        list = self.client.deployments.list()
        self.assertIn(TestDeployment.deployment_uid, str(list))

    def test_06_score(self):
        predictions = self.client.deployments.score(scoring_url=self.scoring_url, payload=self.scoring_data)
        self.assertTrue("prediction" in str(predictions))

    def test_06_score_none_url(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.score(scoring_url=None, payload=self.scoring_data)

    def test_06_score_none_data(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.score(scoring_url=self.scoring_url, payload=None)

    def test_06_score_none_url_and_data(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.score(scoring_url=None, payload=None)

    def test_06_score_empty_url(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.score(scoring_url="", payload=self.scoring_data)

    def test_06_score_empty_json_url(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.score(scoring_url="{}", payload=self.scoring_data)

    def test_06_score_empty_data(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.score(scoring_url=self.scoring_url, payload="")

    def test_06_score_empty_json_data(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.score(scoring_url=self.scoring_url, payload="{}")

    def test_07_delete_deployment_url(self):
        self.client.deployments.delete(deployment_url=TestDeployment.deployment_url_2)

    def test_07_delete_deployment_uid(self):
        self.client.deployments.delete(deployment_uid=TestDeployment.deployment_uid)

    def test_07_delete_deployment_url_repeat(self):
        self.client.deployments.delete(deployment_uid=TestDeployment.deployment_url_2)

    def test_07_delete_deployment_invalid_uid(self):
        with self.assertRaises(WMLClientError):
            self.client.deployments.delete(deployment_uid='146xf7ad-x0x1-4ss4-aaaa-a48xxxxeb787')

    def test_07_delete_deployment_none_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.delete(deployment_url=None)

        self.assertIn("Both deployment_url and deployment_uid", str(context.exception))

    def test_07_delete_deployment_none_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.delete(deployment_uid=None)

        self.assertIn("Both deployment_url and deployment_uid", str(context.exception))

    def test_07_delete_deployment_empty_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.delete(deployment_url="")

        self.assertIn("is not an url", str(context.exception))

    def test_07_delete_deployment_empty_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.delete(deployment_uid="")

        self.assertIn("is not an uid", str(context.exception))

    def test_07_delete_deployment_empty_json_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.delete(deployment_url="{}")

        self.assertIn("is not an url", str(context.exception))

    def test_07_delete_deployment_empty_json_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.delete(deployment_uid="{}")

        self.assertIn("is not an uid", str(context.exception))

    def test_07_delete_deployment_no_para(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.deployments.delete()

        self.assertIn("Both deployment_url and deployment_uid", str(context.exception))


if __name__ == '__main__':
    unittest.main()
