# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import unittest

from ibm_ai_openscale import APIClient
from ibm_ai_openscale.supporting_classes import *
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *
from models_preparation import *
from watson_machine_learning_client import WatsonMachineLearningAPIClient


# @unittest.skipIf(environment != 'YP_ME', "Test could be run only on YP_ME env.")
# @unittest.skipIf(get_wml_instance_plan(get_wml_lite_credentials()) != 'lite', "WML must be in lite plan.")
@unittest.skip
class TestAIOpenScaleClient(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    aios_model_uid = None
    scoring_url = None
    labels = None
    logger = logging.getLogger(__name__)
    ai_client = None
    wml_client = None
    subscription = None
    test_uid = str(uuid.uuid4())

    @classmethod
    def setUpClass(cls):
        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        cls.ai_client = APIClient(cls.aios_credentials)
        cls.wml_credentials = get_wml_credentials()

        prepare_env(cls.ai_client)

    def test_01_check_wml_before_binding(self):
        wml_client = WatsonMachineLearningAPIClient(self.wml_credentials)
        wml_instance_details = wml_client.service_instance.get_details()
        self.assertEqual('lite', wml_instance_details['entity']['plan'])
        self.assertEqual(5000, wml_instance_details['entity']['usage']['prediction_count']['limit'])

        wml_deployments = wml_client.deployments.get_details()
        for deployment in wml_deployments['resources']:
            wml_client.deployments.delete(deployment['metadata']['guid'])

    def test_02_create_client(self):
        TestAIOpenScaleClient.ai_client = APIClient(self.aios_credentials)

    def test_03_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.postgres_credentials, schema=get_schema_name())

    def test_04_bind_wml_instance(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.add("My WML instance", WatsonMachineLearningInstance(self.wml_credentials))

    def test_05_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

        TestAIOpenScaleClient.wml_client.service_instance.get_details()
        print(TestAIOpenScaleClient.wml_client.service_instance.get_details())

    def test_06_check_wml_after_binding(self):
        wml_client = WatsonMachineLearningAPIClient(self.wml_credentials)
        wml_instance_details = wml_client.service_instance.get_details()
        print(wml_instance_details)
        self.assertEqual('lite', wml_instance_details['entity']['plan'])
        self.assertEqual(1000000, wml_instance_details['entity']['usage']['prediction_count']['limit'])

    def test_07_prepare_deployment(self):
        model_data = create_spark_mllib_model_data()

        model_props = {self.wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                       self.wml_client.repository.ModelMetaNames.NAME: "test_" + self.test_uid
                       }

        published_model = self.wml_client.repository.store_model(model=model_data['model'], meta_props=model_props,
                                                                 training_data=model_data['training_data'],
                                                                 pipeline=model_data['pipeline'])
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model)

        print('Stored model: ', TestAIOpenScaleClient.model_uid)

        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name="Test deployment",
                                                        asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

    def test_08_subscribe(self):
        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.aios_model_uid = subscription.uid

    def test_09_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.aios_model_uid)

    def test_10_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_12_score(self):
        deployment_details = self.wml_client.deployments.get_details(TestAIOpenScaleClient.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        payload_scoring = {"fields": ["GENDER", "AGE", "MARITAL_STATUS", "PROFESSION"],
                           "values": [
                               ["M", 23, "Single", "Student"],
                               ["M", 50, "Single", "Executive"],
                               ["M", 70, "Single", "Student"],
                               ["M", 20, "Single", "Executive"],
                               ["M", 23, "Single", "Student"],
                               ["M", 55, "Single", "Executive"],
                               ["M", 70, "Single", "Student"],
                               ["M", 60, "Single", "Executive"]
                           ]
                           }

        for i in range(0, 1000):
            print('SCORING_RESULT {}: {}'.format(i, self.wml_client.deployments.score(scoring_endpoint, payload_scoring)))
            time.sleep(0.01)
            print('SCORING_RESULT {}: {}'.format(i, self.wml_client.deployments.score(scoring_endpoint, payload_scoring)))
            time.sleep(0.01)

    def test_18_unsubscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(TestAIOpenScaleClient.subscription.uid)

    def test_20_unbind(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.delete(TestAIOpenScaleClient.subscription.binding_uid)
        time.sleep(60)

    def test_22_check_wml_after_unbinding(self):
        wml_client = WatsonMachineLearningAPIClient(self.wml_credentials)
        wml_instance_details = wml_client.service_instance.get_details()
        print(wml_instance_details)
        self.assertEqual('lite', wml_instance_details['entity']['plan'])
        self.assertEqual(5000, wml_instance_details['entity']['usage']['prediction_count']['limit'])

    def test_23_bind_wml_instance(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.add("My WML instance", WatsonMachineLearningInstance(self.wml_credentials))

    def test_24_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

        TestAIOpenScaleClient.wml_client.service_instance.get_details()
        print(TestAIOpenScaleClient.wml_client.service_instance.get_details())

    def test_25_check_wml_after_binding(self):
        wml_client = WatsonMachineLearningAPIClient(self.wml_credentials)
        wml_instance_details = wml_client.service_instance.get_details()
        print(wml_instance_details)
        self.assertEqual('lite', wml_instance_details['entity']['plan'])
        self.assertEqual(1000000, wml_instance_details['entity']['usage']['prediction_count']['limit'])

    def test_26_subscribe(self):
        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.aios_model_uid = subscription.uid

    def test_27_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(
            TestAIOpenScaleClient.aios_model_uid)

    def test_28_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_29_score(self):
        deployment_details = self.wml_client.deployments.get_details(TestAIOpenScaleClient.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        payload_scoring = {"fields": ["GENDER", "AGE", "MARITAL_STATUS", "PROFESSION"],
                           "values": [
                               ["M", 23, "Single", "Student"],
                               ["M", 50, "Single", "Executive"],
                               ["M", 70, "Single", "Student"],
                               ["M", 20, "Single", "Executive"],
                               ["M", 23, "Single", "Student"],
                               ["M", 55, "Single", "Executive"],
                               ["M", 70, "Single", "Student"],
                               ["M", 60, "Single", "Executive"]
                           ]
                           }

        for i in range(0, 20):
            print(
                'SCORING_RESULT {}: {}'.format(i, self.wml_client.deployments.score(scoring_endpoint, payload_scoring)))
            time.sleep(0.01)
            print(
                'SCORING_RESULT {}: {}'.format(i, self.wml_client.deployments.score(scoring_endpoint, payload_scoring)))
            time.sleep(0.01)

    def test_30_unsubscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(TestAIOpenScaleClient.subscription.uid)

    def test_31_unbind(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.delete(TestAIOpenScaleClient.subscription.binding_uid)

    def test_32_check_wml_after_unbinding(self):
        wml_client = WatsonMachineLearningAPIClient(self.wml_credentials)
        wml_instance_details = wml_client.service_instance.get_details()
        print(wml_instance_details)
        self.assertEqual('lite', wml_instance_details['entity']['plan'])
        self.assertEqual(5000, wml_instance_details['entity']['usage']['prediction_count']['limit'])

    def test_33_delete_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.delete()
        delete_schema(get_postgres_credentials(), get_schema_name())

    def test_34_check_wml_after_unbinding(self):
        wml_client = WatsonMachineLearningAPIClient(self.wml_credentials)
        wml_instance_details = wml_client.service_instance.get_details()
        print(wml_instance_details)
        self.assertEqual('lite', wml_instance_details['entity']['plan'])
        self.assertEqual(5000, wml_instance_details['entity']['usage']['prediction_count']['limit'])


if __name__ == '__main__':
    unittest.main()
