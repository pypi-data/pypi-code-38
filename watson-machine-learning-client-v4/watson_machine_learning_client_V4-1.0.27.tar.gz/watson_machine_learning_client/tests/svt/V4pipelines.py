import unittest

from watson_machine_learning_client.log_util import get_logger
from preparation_and_cleaning import *
from models_preparation import *


class TestAIFunction(unittest.TestCase):
    runtime_uid = None
    lib_uid = None
    deployment_uid = None
    pipeline_uid = None
    scoring_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestAIFunction.logger.info("Service Instance: setting up credentials")
        self.lib_filepath = os.path.join(os.getcwd(), 'artifacts', 'ai_function.gz')
        self.wml_credentials = get_wml_credentials()
        self.client = get_client()

        self.function_name = 'sample v4 pipeline'
        self.deployment_name = "Test deployment"

    def test_01_service_instance_details(self):
        TestAIFunction.logger.info("Check client ...")
        self.assertTrue(self.client.__class__.__name__ == 'WatsonMachineLearningAPIClient')

        TestAIFunction.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestAIFunction.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_02_create_pipeline(self):

        self.client.repository.PipelineMetaNames.show()
        lib_meta = {
            self.client.runtimes.LibraryMetaNames.NAME: "sample v4 pipeline2",
            self.client.runtimes.LibraryMetaNames.PLATFORM:  {"name": "python","versions": ["3.5"]},
            self.client.runtimes.LibraryMetaNames.VERSION: "1",
            self.client.runtimes.LibraryMetaNames.FILEPATH: TestAIFunction.lib_filepath
        }
        lib_details = self.client.runtimes.store_library(lib_meta)
        TestAIFunction.lib_uid = self.client.runtimes.get_library_uid(lib_details)
        metadata = {
            self.client.pipelines.ConfigurationMetaNames.NAME: "sample v4 pipeline",
            self.client.pipelines.ConfigurationMetaNames.DESCRIPTION: "sample description",
            self.client.pipelines.ConfigurationMetaNames.DOCUMENT: {
                "doc_type": "pipeline",
                "version": "2.0",
                "primary_pipeline": "dlaas_only",
                "pipelines": [
                    {
                        "id": "dlaas_only",
                        "runtime_ref": "hybrid",
                        "nodes": [
                            {
                                "id": "training",
                                "type": "model_node",
                                "op": "dl_train",
                                "runtime_ref": "DL",
                                "inputs": [
                                ],
                                "outputs": [],
                                "parameters": {
                                    "name": "tf-mnist",
                                    "description": "Simple MNIST model implemented in TF",
                                    "command": "python3 convolutional_network.py --trainImagesFile ${DATA_DIR}/train-images-idx3-ubyte.gz --trainLabelsFile ${DATA_DIR}/train-labels-idx1-ubyte.gz --testImagesFile ${DATA_DIR}/t10k-images-idx3-ubyte.gz --testLabelsFile ${DATA_DIR}/t10k-labels-idx1-ubyte.gz --learningRate 0.001 --trainingIters 6000",
                                    "model_definition_url": "/v4/libraries"+TestAIFunction.lib_uid,
                                    "compute_configuration_name": "k80",
                                    "compute_configuration_nodes": 1,
                                    "target_bucket": "wml-dev-results"
                                }
                            }
                        ]
                    }
                ],
                "schemas": [
                    {
                        "id": "schema1",
                        "fields": [
                            {
                                "name": "text",
                                "type": "string"
                            }
                        ]
                    }
                ],
                "runtimes": [
                    {
                        "id": "DL",
                        "name": "tensorflow",
                        "version": "1.5-py3"
                    }
                ]
            }

        }
        pipeline_details = self.client.pipelines.store(metadata)
        TestAIFunction.pipeline_uid = self.client.pipelines.get_uid(pipeline_details)



    def test_03_update_pipeline(self):
        pipeline_props = {
            self.client.repository.FunctionMetaNames.NAME: 'new pipeline',
        }

        details = self.client.pipelines.update(TestAIFunction.pipeline_uid, pipeline_props)
        self.assertFalse('sample v4 pipeline' in json.dumps(details))

    def test_05_get_details(self):

        details = self.client.pipelines.get_details(self.pipeline_uid)
        self.assertTrue(self.function_name in str(details))

    def test_06_list(self):

        self.client.pipelines.list()

    def test_07_create_deployment(self):
        TestAIFunction.logger.info("Create deployment")
        deployment = self.client.deployments.create(artifact_uid=TestAIFunction.function_uid, name=self.deployment_name, asynchronous=False)
        TestAIFunction.logger.debug("Online deployment: " + str(deployment))
        TestAIFunction.scoring_url = self.client.deployments.get_scoring_url(deployment)
        TestAIFunction.logger.debug("Scoring url: {}".format(TestAIFunction.scoring_url))
        TestAIFunction.deployment_uid = self.client.deployments.get_uid(deployment)
        TestAIFunction.logger.debug("Deployment uid: {}".format(TestAIFunction.deployment_uid))
        self.client.deployments.list()
        self.assertTrue("online" in str(deployment))

    def test_08_update_deployment(self):
        self.client.deployments.update(TestAIFunction.deployment_uid)

    def test_09_get_deployment_details(self):
        TestAIFunction.logger.info("Get deployment details")
        deployment_details = self.client.deployments.get_details()
        TestAIFunction.logger.debug("Deployment details: {}".format(deployment_details))
        self.assertTrue(self.deployment_name in str(deployment_details))

    def test_10_score(self):
        scoring_data = {"fields": ["x","y"],"values": [[2.0, 2.0],[99.0,99.0]]}
        predictions = self.client.deployments.score(TestAIFunction.scoring_url, scoring_data)
        print("Predictions: {}".format(predictions))
        self.assertTrue("values" in str(predictions))

    def test_11_delete_deployment(self):
        TestAIFunction.logger.info("Delete deployment")
        self.client.deployments.delete(TestAIFunction.deployment_uid)

    def test_12_delete_pipeline(self):

        TestAIFunction.logger.info("Delete function")
        self.client.pipelines.delete(TestAIFunction.pipeline_uid)
        self.client.runtimes.delete_library(TestAIFunction.lib_uid)


if __name__ == '__main__':
    unittest.main()
