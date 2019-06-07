# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import time
import unittest
from assertions import *

from sklearn import datasets
from sklearn import preprocessing
from sklearn import svm
from sklearn.pipeline import Pipeline

from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes.enums import ProblemType
from preparation_and_cleaning import *


class TestAIOpenScaleClient(unittest.TestCase):

    ai_client = None
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    scoring_url = None
    labels = None
    wml_client = None
    subscription = None
    binding_uid = None
    aios_model_uid = None
    scoring_result = None
    payload_scoring = None
    published_model_details = None
    source_uid = None
    scoring_records = 15
    feedback_records = 10

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
        assert_datamart_details(details=details, schema=self.schema)

    def test_03_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))

        print("Binding details:\n{}".format(self.ai_client.data_mart.bindings.get_details(self.binding_uid)))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_05_prepare_deployment(self):
        asset_name = "AIOS Scikit Digits Model"
        deployment_name = "AIOS Scikit Digits Deployment"
        model_data = datasets.load_digits()
        scaler = preprocessing.StandardScaler()
        clf = svm.SVC(kernel='rbf', probability=True)
        pipeline = Pipeline([('scaler', scaler), ('svc', clf)])
        model = pipeline.fit(model_data.data, model_data.target)
        predicted = model.predict(model_data.data[1: 10])
        predicted_probs = model.predict_proba(model_data.data[1: 10])

        model_meta_props = {
            self.wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
            self.wml_client.repository.ModelMetaNames.NAME: asset_name,
            self.wml_client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: {},
            self.wml_client.repository.ModelMetaNames.EVALUATION_METHOD: "multiclass",
            self.wml_client.repository.ModelMetaNames.EVALUATION_METRICS: [
                {
                    "name": "accuracy",
                    "value": 0.64,
                    "threshold": 0.8
                }
            ]
        }

        print("Publishing a new model...")
        published_model_details = self.wml_client.repository.store_model(model=model, meta_props=model_meta_props, training_data=model_data.data, training_target=model_data.target)

        print("Published model details:\n{}".format(published_model_details))
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        print("Deploying model: {}, deployment name: {}".format(asset_name, deployment_name))
        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name, asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        print("Deployment details:\n{}".format(deployment_details))

    def test_06_subscribe(self):
        # get_details_from_restapi(ai_client=self.ai_client, binding_uid=self.binding_uid)

        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(
                source_uid=self.model_uid,
                problem_type=ProblemType.MULTICLASS_CLASSIFICATION,
                prediction_column='prediction'))
        self.assertIsNotNone(self.subscription)
        TestAIOpenScaleClient.subscription_uid = self.subscription.uid

    def test_07_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)

        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        print("Subscription details:\n{}".format(subscription_details))

    def test_08_list_deployments(self):
        print("Listing deployments:\n")
        self.subscription.list_deployments()

    def test_09_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details, payload=True, performance=True)

    def test_10_get_performance_monitoring_details(self):
        performance_monitoring_details = self.subscription.performance_monitoring.get_details()
        assert_performance_monitoring_configuration(performance_monitoring_details=performance_monitoring_details)

    def test_11_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        payload_scoring = {"values": [
            [0, 0, 5, 16, 16, 3, 0, 0, 0, 0, 9, 16, 7, 0, 0, 0, 0, 0, 12, 15, 2, 0, 0, 0, 0, 1, 15, 16, 15, 4, 0, 0, 0, 0,
             9, 13, 16, 9, 0, 0, 0, 0, 0, 0, 14, 12, 0, 0, 0, 0, 5, 12, 16, 8, 0, 0, 0, 0, 3, 15, 15, 1, 0, 0],
            [0, 0, 6, 16, 12, 1, 0, 0, 0, 0, 5, 16, 13, 10, 0, 0, 0, 0, 0, 5, 5, 15, 0, 0, 0, 0, 0, 0, 8, 15, 0, 0, 0, 0, 0,
             0, 13, 13, 0, 0, 0, 0, 0, 6, 16, 9, 4, 1, 0, 0, 3, 16, 16, 16, 16, 10, 0, 0, 5, 16, 11, 9, 6, 2]]}

        TestAIOpenScaleClient.scoring_records = 30
        for i in range(0, int(self.scoring_records/2)):
            TestAIOpenScaleClient.scoring_result = self.wml_client.deployments.score(scoring_endpoint, payload_scoring)
            print("Scoring result: {}".format(self.scoring_result))
            self.assertIsNotNone(self.scoring_result)

        # scoring_result = self.wml_client.deployments.score(scoring_endpoint, payload_scoring)
        # request, response, response_time = (payload_scoring, scoring_result, 5)
        # records_list = []
        # from ibm_ai_openscale.supporting_classes.payload_record import PayloadRecord
        #
        # for i in range(1, 10):
        #     records_list.append(PayloadRecord(request=request, response=response, response_time=int(response_time)))
        #
        # TestAIOpenScaleClient.subscription.payload_logging.store(records=records_list)

        waiting_time = 60
        print("Waiting {} seconds for propagation.".format(waiting_time))
        time.sleep(waiting_time)

    def test_12_stats_on_performance_monitoring_table(self):
        if "ICP" in get_env():
            self.skipTest("Performance monitoring is not working on ICP with WML scoring.")

        self.subscription.performance_monitoring.print_table_schema()
        self.subscription.performance_monitoring.show_table()
        self.subscription.performance_monitoring.describe_table()
        self.subscription.performance_monitoring.get_table_content()

        performance_metrics = self.subscription.performance_monitoring.get_table_content(format='python')
        print("Performance metrics:\n{}".format(performance_metrics))
        self.assertGreater(len(performance_metrics['values']), 0)

    def test_13_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        self.subscription.payload_logging.show_table()
        self.subscription.payload_logging.describe_table()

        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content, scoring_records=self.scoring_records)

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        assert_payload_logging_python_table_content(python_table_content=python_table_content, fields=['prediction', 'probability'])

    def test_14_enable_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.enable(threshold=0.7, min_records=5)

        details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        assert_quality_monitoring_configuration(quality_monitoring_details=details)

    def test_15_feedback_logging(self):

        print(self.subscription.get_details())
        records = []

        feedback_payload = [0, 0, 5, 16, 16, 3, 0, 0, 0, 0, 9, 16, 7, 0, 0, 0, 0, 0, 12, 15, 2, 0, 0, 0, 0, 1, 15, 16, 15, 4, 0, 0, 0,
                            0, 9, 13, 16, 9, 0, 0, 0, 0, 0, 0, 14, 12, 0, 0, 0, 0, 5, 12, 16, 8, 0, 0, 0, 0, 3, 15, 15, 1, 0, 0, 2]

        for i in range(0, 10):
            records.append(feedback_payload)
        TestAIOpenScaleClient.subscription.feedback_logging.store(feedback_data=records)

        print("Waiting 30 seconds for propagation...")
        time.sleep(30)

    def test_16_stats_on_feedback_logging(self):
        TestAIOpenScaleClient.subscription.feedback_logging.show_table()
        TestAIOpenScaleClient.subscription.feedback_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.feedback_logging.describe_table()

    def test_17_run_quality_monitoring(self):
        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run()
        assert_quality_run(run_details=run_details)

        status = run_details['status']
        id = run_details['id']
        start_time = time.time()
        elapsed_time = 0

        while status != 'completed' and elapsed_time < 60:
            time.sleep(10)
            run_details = TestAIOpenScaleClient.subscription.quality_monitoring.get_run_details(run_uid=id)
            status = run_details['status']
            elapsed_time = time.time() - start_time
            print("Run details: {}".format(run_details))
            self.assertNotIn('failed', status)

        self.assertTrue('completed' in status)

    def test_18_stats_on_quality_monitoring_table(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table(limit=None)
        TestAIOpenScaleClient.subscription.quality_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content()
        quality_metrics = TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue(len(quality_metrics['values']) > 0)

    def test_19_disable_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.payload_logging.disable()
        TestAIOpenScaleClient.subscription.performance_monitoring.disable()
        TestAIOpenScaleClient.subscription.quality_monitoring.disable()

    def test_21_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_22_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()

        for deployment in cls.wml_client.deployments.get_details()['resources']:
            if 'published_model' in deployment['entity'] and cls.model_uid == deployment['entity']['published_model']['guid']:
                print("Deleting deployment: {}".format(deployment['metadata']['guid']))
                cls.wml_client.deployments.delete(deployment['metadata']['guid'])
        cls.wml_client.repository.delete(cls.model_uid)
        print("Deleting model: {}".format(cls.model_uid))


if __name__ == '__main__':
    unittest.main()


