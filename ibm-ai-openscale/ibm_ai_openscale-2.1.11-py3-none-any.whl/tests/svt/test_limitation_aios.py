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


@unittest.skipIf(get_aios_lite_credentials() is None, "AIOS lite instance is not available. Please fill `aios_lite_credentials` field with proper credentials.")
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

    wml_models = []
    subscriptions = []

    @classmethod
    def setUpClass(cls):
        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        cls.ai_client = APIClient(cls.aios_credentials)
        cls.wml_credentials = get_wml_credentials()

        cls.wml_client = WatsonMachineLearningAPIClient(cls.wml_credentials)

        prepare_env(cls.ai_client)

    def test_01_check_number_of_models_and_deployments(self):

        # clean up all models
        # for asset in self.wml_client.repository.get_details()['models']['resources']:
        #     for deployment in self.wml_client.deployments.get_details()['resources']:
        #         if 'published_model' in deployment['entity'] and asset['metadata']['guid'] == deployment['entity']['published_model']['guid']:
        #             print("Deleting deployment: {}".format(deployment['metadata']['guid']))
        #             self.wml_client.deployments.delete(deployment['metadata']['guid'])
        #     self.wml_client.repository.delete(asset['metadata']['guid'])
        #     print("Deleting model: {}".format(asset['metadata']['guid']))

        for asset in self.wml_client.repository.get_details()['models']['resources']:
            if asset['metadata']['guid'] not in self.wml_models:
                TestAIOpenScaleClient.wml_models.append(asset['metadata']['guid'])

        #publish first model for quality monitoring
        model_data = create_spark_mllib_model_data()
        model_props = {
            self.wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
            self.wml_client.repository.ModelMetaNames.NAME: "test_" + self.test_uid
        }

        published_model = self.wml_client.repository.store_model(model=model_data['model'], meta_props=model_props, training_data=model_data['training_data'], pipeline=model_data['pipeline'])
        print("Published model quality details:\n{}".format(published_model))
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model)
        print('Stored model for quality: ', self.model_uid)
        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name="Limitation deployment Quality", asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        if len(self.wml_models) < 6:
            print("Number of deployment is less than 5 ({}). Creating the new ones.".format(len(self.wml_models)))

            for i in range(0, (6-len(self.wml_models))):
                model_props = {
                    self.wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                    self.wml_client.repository.ModelMetaNames.NAME: "test_" + self.test_uid
                }

                published_model = self.wml_client.repository.store_model(model=model_data['model'], meta_props=model_props,
                                                                         training_data=model_data['training_data'],
                                                                         pipeline=model_data['pipeline'])
                model_uid = self.wml_client.repository.get_model_uid(published_model)
                print('Stored model: ', model_uid)
                TestAIOpenScaleClient.wml_models.append(model_uid)

                self.wml_client.deployments.create(artifact_uid=model_uid, name="Limitation deployment", asynchronous=False)

        else:
            print("Number of deployment is higher than 5 ({}). Continue testing.".format(len(self.wml_models)))

    def test_02_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=get_schema_name())
        print("Datamart details:\n{}".format(TestAIOpenScaleClient.ai_client.data_mart.get_details()))

    def test_03_bind_wml_instance(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.add("My WML instance", WatsonMachineLearningInstance(self.wml_credentials))

    def test_04_subscribe_more_than_5_models(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(
                source_uid=self.model_uid,
                problem_type=ProblemType.MULTICLASS_CLASSIFICATION,
                input_data_type=InputDataType.STRUCTURED,
                prediction_column='predictedLabel'
            )
        )
        print('Subscription details: ' + str(self.subscription.get_details()))
        TestAIOpenScaleClient.subscriptions.append(TestAIOpenScaleClient.subscription.uid)

        for model_uid in self.wml_models:
            try:
                subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(model_uid))
                print('Subscription details: ' + str(subscription.get_details()))
                TestAIOpenScaleClient.subscriptions.append(subscription.uid)
            except ApiRequestFailure as e:
                print(e)
                self.assertIn("Quota exceeded on resource", e.error_msg)
                break

        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.list()
        self.assertEqual(5, len(self.subscriptions))

    def test_05_list_deployments_for_subscriptions(self):
        for subscription_uid in self.subscriptions:
            subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(subscription_uid=subscription_uid)
            subscription.list_deployments()

    def test_06_score(self):
        deployment_details = self.wml_client.deployments.get_details(TestAIOpenScaleClient.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        payload_scoring = {
            "fields": ["GENDER", "AGE", "MARITAL_STATUS", "PROFESSION"],
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

        for i in range(0, 10):
            print('SCORING_RESULT {}: {}'.format(i, self.wml_client.deployments.score(scoring_endpoint, payload_scoring)))

        print("Waiting 20 seconds for propagation.")
        time.sleep(20)

    def test_07_enable_quality_monitoring(self):
        self.subscription.quality_monitoring.enable(threshold=0.7, min_records=10)
        details = self.subscription.quality_monitoring.get_details()
        print(details)
        self.assertIn('True', str(details))

    def test_08_feedback_logging(self):
        self.skipTest("Do not consume all feedback :)")

        fields = ["GENDER", "AGE", "MARITAL_STATUS", "PROFESSION", "PRODUCT_LINE"]
        record = ["M", 23, "Single", "Student", "Golf Equipment"]

        records = []
        for j in range(0, 60):
            records.append(record)

        print("Sending feedback...")
        for i in range(0, 1000):
            try:
                TestAIOpenScaleClient.subscription.feedback_logging.store(feedback_data=records, fields=fields)
            except ApiRequestFailure as e:
                print(e)
                self.assertIn("Quota exceeded on resource", e.error_msg)
                break
            time.localtime(0.1)
            print("".format(i), end=" ,", flush=True)

    def test_09_stats_on_feedback_logging(self):

        feedback_pd = TestAIOpenScaleClient.subscription.feedback_logging.get_table_content(format='pandas')
        print(feedback_pd)

        TestAIOpenScaleClient.subscription.feedback_logging.show_table()
        TestAIOpenScaleClient.subscription.feedback_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.feedback_logging.describe_table()

    def test_10_run_quality_monitoring(self):
        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run()
        self.assertTrue('Prerequisite check' in str(run_details))

        status = run_details['status']
        id = run_details['id']
        start_time = time.time()
        elapsed_time = 0

        while status is not 'completed' and elapsed_time < 60:
            time.sleep(10)
            run_details = TestAIOpenScaleClient.subscription.quality_monitoring.get_run_details(run_uid=id)
            status = run_details['status']
            elapsed_time = time.time() - start_time

        self.assertTrue('completed' in status)

    def test_11_unsubscribe(self):
        for subscription_uid in self.subscriptions:
            TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(subscription_uid=subscription_uid)

    def test_12_delete_quality_deployment(self):
        self.wml_client.deployments.delete(self.deployment_uid)
        self.wml_client.repository.delete(self.model_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
