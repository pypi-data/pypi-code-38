# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import unittest
import time
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *


@unittest.skip("skipped")
class TestAIOpenScaleClient(unittest.TestCase):
    model_uid = None
    deployment_1_uid = None
    deployment_2_uid = None
    deployment_3_uid = None
    scoring_1_url = None
    scoring_2_url = None
    scoring_3_url = None
    subscription_uid = None
    labels = None
    ai_client = None
    wml_client = None
    subscription = None
    binding_uid = None
    test_uid = str(uuid.uuid4())

    @classmethod
    def setUpClass(cls):
        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        if "ICP" in get_env():
            cls.ai_client = APIClient4ICP(cls.aios_credentials)
        else:
            cls.ai_client = APIClient(cls.aios_credentials)
            cls.wml_credentials = get_wml_credentials()

        prepare_env(cls.ai_client)

    def test_01_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_02_data_mart_get_details(self):
        details = TestAIOpenScaleClient.ai_client.data_mart.get_details()
        print(details)
        self.assertTrue(len(json.dumps(details)) > 10)

    def test_03_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud",WatsonMachineLearningInstance(self.wml_credentials))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(
            binding_uid)

    def test_05_publish_model(self):
        model_name = "AIOS Keras mnist model"
        wml_models = self.wml_client.repository.get_details()

        for model in wml_models['models']['resources']:
            if model_name == model['entity']['name']:
                TestAIOpenScaleClient.model_uid = model['metadata']['guid']
                break

        if self.model_uid is None:
            print("Storing model ...")
            published_model = self.model.publish_to_wml(self.wml_client)
            self.assertIsNotNone(published_model)

            TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model)

        print("Model id: {}".format(self.model_uid))

    def test_06a_create_1_deployment(self):
        deployment_name = "AIOS Keras mnist deployment 11"

        wml_deployments = self.wml_client.deployments.get_details()

        for deployment in wml_deployments['resources']:
            if deployment_name == deployment['entity']['name']:
                TestAIOpenScaleClient.deployment_1_uid = deployment['metadata']['guid']
                break

        if self.deployment_1_uid is None:
            print("Deploying model...")

            deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name, asynchronous=False)
            TestAIOpenScaleClient.deployment_1_uid = self.wml_client.deployments.get_uid(deployment)

        print("Deployment id 1: {}".format(self.deployment_1_uid))

    def test_06b_create_2_deployment(self):
        deployment_name = "AIOS Keras mnist deployment 12"

        wml_deployments = self.wml_client.deployments.get_details()

        for deployment in wml_deployments['resources']:
            if deployment_name == deployment['entity']['name']:
                TestAIOpenScaleClient.deployment_2_uid = deployment['metadata']['guid']
                break

        if self.deployment_2_uid is None:
            print("Deploying model...")

            deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name,
                                                            asynchronous=False)
            TestAIOpenScaleClient.deployment_2_uid = self.wml_client.deployments.get_uid(deployment)

        print("Deployment id 2: {}".format(self.deployment_2_uid))

    def test_06c_create_3_deployment(self):
        deployment_name = "AIOS Keras mnist deployment 13"

        wml_deployments = self.wml_client.deployments.get_details()

        for deployment in wml_deployments['resources']:
            if deployment_name == deployment['entity']['name']:
                TestAIOpenScaleClient.deployment_3_uid = deployment['metadata']['guid']
                break

        if self.deployment_3_uid is None:
            print("Deploying model...")

            deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name,
                                                            asynchronous=False)
            TestAIOpenScaleClient.deployment_3_uid = self.wml_client.deployments.get_uid(deployment)

        print("Deployment id 3: {}".format(self.deployment_3_uid))

    def test_07_subscribe(self):
        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.subscription_uid = subscription.uid

    def test_08_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(
            TestAIOpenScaleClient.subscription_uid)
        print(str(TestAIOpenScaleClient.subscription.get_details()))

    def test_09_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_10_setup_payload_logging(self):
        TestAIOpenScaleClient.subscription.payload_logging.enable()
        print('Subscription details after payload logging ON: ' + str(
            TestAIOpenScaleClient.subscription.get_details()))

    def test_11_get_payload_logging_details(self):
        TestAIOpenScaleClient.subscription.payload_logging.get_details()

    def test_12_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_1_uid)
        scoring_endpoint_1 = self.wml_client.deployments.get_scoring_url(deployment_details)

        for i in range(0, 10):
            scoring_payload = self.model.get_scoring_payload()
            scores = self.wml_client.deployments.score(scoring_url=scoring_endpoint_1, payload=scoring_payload)
            self.assertIsNotNone(scores)

        deployment_details = self.wml_client.deployments.get_details(self.deployment_2_uid)
        scoring_endpoint_2 = self.wml_client.deployments.get_scoring_url(deployment_details)

        for i in range(0, 10):
            scoring_payload = self.model.get_scoring_payload()
            scores = self.wml_client.deployments.score(scoring_url=scoring_endpoint_2, payload=scoring_payload)
            self.assertIsNotNone(scores)

        deployment_details = self.wml_client.deployments.get_details(self.deployment_3_uid)
        scoring_endpoint_3 = self.wml_client.deployments.get_scoring_url(deployment_details)

        for i in range(0, 10):
            scoring_payload = self.model.get_scoring_payload()
            scores = self.wml_client.deployments.score(scoring_url=scoring_endpoint_3, payload=scoring_payload)
            self.assertIsNotNone(scores)

        time.sleep(20)

    def test_13_stats_on_payload_logging_table(self):
        TestAIOpenScaleClient.subscription.payload_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.payload_logging.show_table()
        TestAIOpenScaleClient.subscription.payload_logging.describe_table()
        TestAIOpenScaleClient.subscription.payload_logging.get_table_content()
        performance_metrics = TestAIOpenScaleClient.subscription.payload_logging.get_table_content(format='python')
        self.assertTrue(len(performance_metrics['values']) > 0)

    def test_15_get_performance_monitor_details(self):
        TestAIOpenScaleClient.subscription.performance_monitoring.get_details()

    def test_16_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_1_uid)
        scoring_endpoint_1 = self.wml_client.deployments.get_scoring_url(deployment_details)

        for i in range(0, 10):
            scoring_payload = self.model.get_scoring_payload()
            scores = self.wml_client.deployments.score(scoring_url=scoring_endpoint_1, payload=scoring_payload)
            self.assertIsNotNone(scores)

        time.sleep(20)

    def test_17_stats_on_performance_monitoring_table(self):
        TestAIOpenScaleClient.subscription.performance_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.performance_monitoring.show_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content()
        performance_metrics = TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content(format='python')
        self.assertTrue(len(performance_metrics['values']) > 0)

    def test_18_disable_performance_monitoring(self):
        TestAIOpenScaleClient.subscription.performance_monitoring.disable()

    def test_19_disable_payload_logging(self):
        TestAIOpenScaleClient.subscription.payload_logging.disable()

    def test_20_get_metrics(self):
        print(TestAIOpenScaleClient.subscription.performance_monitoring.get_metrics(deployment_uid=TestAIOpenScaleClient.deployment_1_uid))

        self.assertTrue(len(TestAIOpenScaleClient.subscription.performance_monitoring.get_metrics(deployment_uid=TestAIOpenScaleClient.deployment_1_uid)['metrics']) > 0)

    def test_21_unsubscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(TestAIOpenScaleClient.subscription.uid)

    def test_22_unbind(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.delete(TestAIOpenScaleClient.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()