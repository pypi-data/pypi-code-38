import unittest

from watson_machine_learning_client.log_util import get_logger
from preparation_and_cleaning import *
from models_preparation import *


class TestAIFunction(unittest.TestCase):
    runtime_uid = None
    deployment_uid = None
    function_uid = None
    scoring_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestAIFunction.logger.info("Service Instance: setting up credentials")

        self.wml_credentials = get_wml_credentials()
        self.client = get_client()

        self.function_name = 'simplest AI function'
        self.deployment_name = "Test deployment"

    def test_01_service_instance_details(self):
        TestAIFunction.logger.info("Check client ...")
        self.assertTrue(self.client.__class__.__name__ == 'WatsonMachineLearningAPIClient')

        TestAIFunction.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestAIFunction.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_02_create_ai_function(self):

        self.client.repository.FunctionMetaNames.show()

        function_props = {
            self.client.repository.FunctionMetaNames.NAME: 'xxxx'
        }

        def score(payload):
            values = [[row[0]*row[1]] for row in payload['values']]
            return {'fields': ['multiplication'], 'values': values}

        ai_function_details = self.client.repository.store_function(score, function_props)

        TestAIFunction.function_uid = self.client.repository.get_function_uid(ai_function_details)
        function_url = self.client.repository.get_function_href(ai_function_details)
        TestAIFunction.logger.info("AI function ID:" + str(TestAIFunction.function_uid))
        TestAIFunction.logger.info("AI function URL:" + str(function_url))
        self.assertIsNotNone(TestAIFunction.function_uid)
        self.assertIsNotNone(function_url)
        TestAIFunction.runtime_uid = self.client.runtimes.get_uid(ai_function_details)

    def test_03_update_function(self):
        function_props = {
            self.client.repository.FunctionMetaNames.NAME: 'simplest AI function',
            self.client.repository.FunctionMetaNames.DESCRIPTION: 'desc',
            self.client.repository.FunctionMetaNames.TAGS: [{"value": "ProjectA", "description": "Functions created for ProjectA"}],
            self.client.repository.FunctionMetaNames.INPUT_DATA_SCHEMAS: [{
                "id":"1",
                "type": "struct",
                "fields": [
                    {
                        "name": "x",
                        "type": "double",
                        "nullable": False,
                        "metadata": {}
                    },
                    {
                        "name": "y",
                        "type": "double",
                        "nullable": False,
                        "metadata": {}
                    }
                ]
            }],
            self.client.repository.FunctionMetaNames.OUTPUT_DATA_SCHEMAS: [{
                "id":"1",
                "type": "struct",
                "fields": [
                    {
                        "name": "multiplication",
                        "type": "double",
                        "nullable": False,
                        "metadata": {}
                    }
                ]
            }]
        }

        details = self.client.repository.update_function(TestAIFunction.function_uid, function_props)
        self.assertFalse('xxxx' in json.dumps(details))

    def test_04_download_ai_function_content(self):
        try:
            os.remove('test_ai_function.tar.gz')
        except:
            pass
        self.client.repository.download(TestAIFunction.function_uid, filename='test_ai_function_v41.gz')
        try:
            os.remove('test_ai_function.tar.gz')
        except:
            pass

    def test_05_get_details(self):

        details = self.client.repository.get_function_details(self.function_uid)
        self.assertTrue(self.function_name in str(details))

    def test_06_list(self):
        self.client.repository.list()

        self.client.repository.list_functions()
    def test_07_create_deployment(self):
        deploy_meta = {
                self.client.deployments.ConfigurationMetaNames.NAME: "deployment_Function",
                self.client.deployments.ConfigurationMetaNames.DESCRIPTION: "deployment_description"
            }

        TestAIFunction.logger.info("Create deployment")
        deployment = self.client.deployments.create(artifact_uid=TestAIFunction.function_uid, meta_props=deploy_meta)
        TestAIFunction.logger.debug("deployment: " + str(deployment))
        TestAIFunction.scoring_url = self.client.deployments.get_scoring_href(deployment)
        TestAIFunction.logger.debug("Scoring href: {}".format(TestAIFunction.scoring_url))
        TestAIFunction.deployment_uid = self.client.deployments.get_uid(deployment)
        TestAIFunction.logger.debug("Deployment uid: {}".format(TestAIFunction.deployment_uid))
        self.client.deployments.list()
        self.assertTrue("deployment_Function" in str(deployment))

    def test_08_update_deployment(self):
        patch_meta = {
            self.client.deployments.ConfigurationMetaNames.DESCRIPTION: "deployment_Updated_Function_Description",
        }
        self.client.deployments.update(TestAIFunction.deployment_uid, patch_meta)

    def test_09_get_deployment_details(self):
        TestAIFunction.logger.info("Get deployment details")
        deployment_details = self.client.deployments.get_details()
        TestAIFunction.logger.debug("Deployment details: {}".format(deployment_details))
        self.assertTrue(self.deployment_name in str(deployment_details))

    def test_10_score(self):
        scoring_data = {"input_data":[{"fields": ["x","y"],"values": [[2.0, 2.0],[99.0,99.0]]}]}
        predictions = self.client.deployments.score(TestAIFunction.scoring_url, scoring_data)
        print("Predictions: {}".format(predictions))
        self.assertTrue("values" in str(predictions))

    def test_11_delete_deployment(self):
        TestAIFunction.logger.info("Delete deployment")
        self.client.deployments.delete(TestAIFunction.deployment_uid)

    def test_12_delete_function(self):
        TestAIFunction.logger.info("Delete function")
        self.client.repository.delete(TestAIFunction.function_uid)



if __name__ == '__main__':
    unittest.main()
