# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes import PayloadRecord, InputDataType
from assertions import *


class TestAIOpenScaleClient(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    scoring_url = None
    labels = None
    ai_client = None
    wml_client = None
    binding_uid = None
    subscription = None
    scoring_records = None
    feedback_records = None
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
        assert_datamart_details(details, schema=self.schema)

    def test_03_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))

        print("Binding details:\n{}".format(self.ai_client.data_mart.bindings.get_details(self.binding_uid)))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_05_store_model(self):
        model_name = "AIOS SPSS Customer Model"
        deployment_name = "AIOS SPSS Customer Deployment"

        model_path = os.path.join(os.getcwd(), 'artifacts', 'SPSSCustomerSatisfaction', 'customer-satisfaction-prediction.str')

        model_meta_props = {
                self.wml_client.repository.ModelMetaNames.NAME: model_name,
                self.wml_client.repository.ModelMetaNames.AUTHOR_NAME: "John Smith",
                self.wml_client.repository.ModelMetaNames.FRAMEWORK_NAME: "spss-modeler",
                self.wml_client.repository.ModelMetaNames.FRAMEWORK_VERSION: "18.0",
                self.wml_client.repository.ModelMetaNames.RUNTIME_NAME: "spss-modeler",
                self.wml_client.repository.ModelMetaNames.RUNTIME_VERSION: "18.0"
            }

        print("Publishing a new model...")
        published_model_details = self.wml_client.repository.store_model(model=model_path, meta_props=model_meta_props)

        print("Published model details:\n{}".format(published_model_details))
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        print("Deploying model: {}, deployment name: {}".format(model_name, deployment_name))
        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name, asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        print("Deployment details:\n{}".format(deployment_details))

    def test_06_subscribe(self):
        from ibm_ai_openscale.supporting_classes.enums import ProblemType
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(
                TestAIOpenScaleClient.model_uid,
                problem_type=ProblemType.BINARY_CLASSIFICATION,
                input_data_type=InputDataType.STRUCTURED,
                label_column='Churn',
                prediction_column='Predicted Churn',
                probability_column='Probability of Churn'
            )
        )

    def test_07_get_subscription(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)

        subscription_details = self.subscription.get_details()
        print("Subscription details:\n{}".format(subscription_details))

    def test_08_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details, payload=True, performance=True)

    def test_09_get_payload_logging_details(self):
        payload_logging_details = self.subscription.payload_logging.get_details()
        assert_payload_logging_configuration(payload_logging_details=payload_logging_details)

    def test_10_get_performance_monitoring_details(self):
        performance_monitoring_details = self.subscription.performance_monitoring.get_details()
        assert_performance_monitoring_configuration(performance_monitoring_details=performance_monitoring_details)

    def test_11_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        payload_scoring = {
            "fields": [
                "customerID",
                "gender",
                "SeniorCitizen",
                "Partner",
                "Dependents",
                "tenure",
                "PhoneService",
                "MultipleLines",
                "InternetService",
                "OnlineSecurity",
                "OnlineBackup",
                "DeviceProtection",
                "TechSupport",
                "StreamingTV",
                "StreamingMovies",
                "Contract",
                "PaperlessBilling",
                "PaymentMethod",
                "MonthlyCharges",
                "TotalCharges",
                "Churn",
                "SampleWeight"
            ],
            "values": [
                [
                    "3638-WEABW",
                    "Female",
                    0,
                    "Yes",
                    "No",
                    58,
                    "Yes",
                    "Yes",
                    "DSL",
                    "No",
                    "Yes",
                    "No",
                    "Yes",
                    "No",
                    "No",
                    "Two year",
                    "Yes",
                    "Credit card (automatic)",
                    59.9,
                    3505.1,
                    "No",
                    2.768
                ]
            ]
        }
        print("Payload scoring:\n{}".format(payload_scoring))

        scoring_result = self.wml_client.deployments.score(scoring_endpoint, payload_scoring)
        print("Scoring result: {}".format(scoring_result))
        self.assertIsNotNone(scoring_result)

        TestAIOpenScaleClient.scoring_records = 12

        records_list = []
        for i in range(0, self.scoring_records):
            records_list.append(PayloadRecord(request=payload_scoring, response=scoring_result, response_time=int(20)))

        TestAIOpenScaleClient.subscription.payload_logging.store(records=records_list)

        import time
        print("Waiting 60 seconds for propagation.")
        time.sleep(60)

    def test_12_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        self.subscription.payload_logging.show_table()
        self.subscription.payload_logging.describe_table()

        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content, scoring_records=self.scoring_records)

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        assert_payload_logging_python_table_content(python_table_content=python_table_content, fields=['Predicted Churn', 'Probability of Churn'])

    def test_13_stats_on_performance_monitoring_table(self):
        if "ICP" in get_env():
            self.skipTest("Performance monitoring is not working on ICP with WML scoring.")

        self.subscription.performance_monitoring.print_table_schema()
        self.subscription.performance_monitoring.show_table()
        self.subscription.performance_monitoring.describe_table()

        performance_table_pandas = self.subscription.performance_monitoring.get_table_content()
        assert_performance_monitoring_pandas_table_content(pandas_table_content=performance_table_pandas)

        performance_table_python = self.subscription.performance_monitoring.get_table_content(format='python')
        assert_performance_monitoring_python_table_content(python_table_content=performance_table_python)

    def test_14_enable_quality_monitoring(self):
        self.subscription.quality_monitoring.enable(threshold=0.7, min_records=10)

        details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        assert_quality_monitoring_configuration(quality_monitoring_details=details)

    def test_15_send_feedback_data(self):

        feedback_payload = ["9237-HQITU", "Female", 0, "No", "No", 20, "Yes", "No", "Fiber optic", "No", "No", "No", "No", "No", "No", "Month-to-month", "Yes", "Electronic check",
                            70.7, 1200, "No", 2.748]
        fields = ["customerID", "gender", "SeniorCitizen", "Partner", "Dependents", "tenure", "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup",
                  "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn",
                  "SampleWeight"]

        print("Feedback payload:\n{}".format(feedback_payload))

        TestAIOpenScaleClient.feedback_records = 20
        records = []
        for i in range(0, self.feedback_records):
            records.append(feedback_payload)

        self.subscription.feedback_logging.store(feedback_data=records, fields=fields)

        print("Waiting 20 seconds for records.")
        time.sleep(20)

    def test_16_stats_on_feedback_logging(self):
        self.subscription.feedback_logging.show_table()
        self.subscription.feedback_logging.print_table_schema()
        self.subscription.feedback_logging.describe_table()

        feedback_pd = self.subscription.feedback_logging.get_table_content(format='pandas')
        assert_feedback_pandas_table_content(pandas_table_content=feedback_pd, feedback_records=self.feedback_records)

    def test_17_run_quality_monitor(self):
        self.skipTest(reason="Skipped due to issue: #5484")

        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run()
        assert_quality_run(run_details=run_details)

        status = run_details['status']
        id = run_details['id']
        start_time = time.time()
        elapsed_time = 0

        while status != 'completed' and elapsed_time < 180:
            time.sleep(10)
            run_details = TestAIOpenScaleClient.subscription.quality_monitoring.get_run_details(run_uid=id)
            status = run_details['status']
            elapsed_time = time.time() - start_time
            print("Status: {}\nRun details: {}".format(status, run_details))
            self.assertNotEqual('failed', status)

        self.assertEqual('completed', status)

    def test_18_stats_on_quality_monitoring_table(self):
        self.skipTest(reason="Skipped due to issue: #5484")

        self.subscription.quality_monitoring.print_table_schema()
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_table(limit=None)
        self.subscription.quality_monitoring.describe_table()

        quality_monitoring_table = self.subscription.quality_monitoring.get_table_content()
        assert_quality_monitoring_pandas_table_content(pandas_table_content=quality_monitoring_table)

        quality_metrics = self.subscription.quality_monitoring.get_table_content(format='python')
        assert_quality_monitoring_python_table_content(python_table_content=quality_metrics)

    def test_19_get_metrics(self):
        self.skipTest(reason="Skipped due to issue: #5484")

        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics())
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(
            deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(
            subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(
            asset_uid=TestAIOpenScaleClient.subscription.source_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(
            asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type='performance'))
        print(TestAIOpenScaleClient.subscription.performance_monitoring.get_metrics(
            deployment_uid=TestAIOpenScaleClient.deployment_uid))

        self.assertTrue(
            len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics()['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(
            deployment_uid=TestAIOpenScaleClient.deployment_uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(
            subscription_uid=TestAIOpenScaleClient.subscription.uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(
            asset_uid=TestAIOpenScaleClient.subscription.source_uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(
            asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type='performance')['deployment_metrics'][
                                0]['metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.subscription.performance_monitoring.get_metrics(
            deployment_uid=TestAIOpenScaleClient.deployment_uid)['metrics']) > 0)

    def test_20_unsubscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(TestAIOpenScaleClient.subscription.uid)

    def test_21_unbind(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.delete(TestAIOpenScaleClient.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()

        clean_wml_instance(model_id=cls.model_uid, deployment_id=cls.deployment_uid, binding_id=cls.binding_uid)


if __name__ == '__main__':
    unittest.main()
