# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import glob

from keras_preprocessing.image import load_img, img_to_array

from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes.enums import FeedbackFormat, ProblemType, InputDataType


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
    scoring_result = None
    scoring_records = None
    feedback_records = None

    model_path = os.path.join(os.getcwd(), 'artifacts', 'dogs-vs-cats', 'dogs-vs-cats-model.h5.tgz')

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

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(
            binding_uid)

    def test_05_prepare_deployment(self):
        model_name = "AIOS Keras DogsAndCats model"
        deployment_name = "AIOS Keras DogsAndCats deployment"

        print("Storing model ...")

        model_props = {
            self.wml_client.repository.ModelMetaNames.NAME: "{}".format(model_name),
            self.wml_client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.wml_client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
            self.wml_client.repository.ModelMetaNames.RUNTIME_NAME: "python",
            self.wml_client.repository.ModelMetaNames.RUNTIME_VERSION: "3.6",
            self.wml_client.repository.ModelMetaNames.FRAMEWORK_LIBRARIES: [{'name': 'keras', 'version': '2.2.4'}],
        }

        published_model_details = self.wml_client.repository.store_model(model=self.model_path, meta_props=model_props)
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        print("Deploying model...")

        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name, asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        print("Model id: {}".format(self.model_uid))
        print("Deployment id: {}".format(self.deployment_uid))

    def test_06_subscribe(self):
        # get_details_from_restapi(ai_client=self.ai_client, binding_uid=self.binding_uid)

        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(
                source_uid=self.model_uid,
                binding_uid=self.binding_uid,
                problem_type=ProblemType.BINARY_CLASSIFICATION,
                input_data_type=InputDataType.UNSTRUCTURED_IMAGE,
                label_column='label'
            )
        )
        TestAIOpenScaleClient.aios_model_uid = subscription.uid

    def test_07_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.aios_model_uid)
        print("Subscription details: {}".format(self.subscription.get_details()))

    def test_08_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_09_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details, payload=True, performance=True)

    def test_10_get_payload_logging_details(self):
        TestAIOpenScaleClient.subscription.payload_logging.get_details()

    def test_11_get_performance_monitor_details(self):
        TestAIOpenScaleClient.subscription.performance_monitoring.get_details()

    def test_12_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        images = []
        for file in glob.glob("datasets/dogs-vs-cats/scoring-data/*.jpg"):
            test_image = load_img(file, target_size=(150, 150))
            test_image_array = img_to_array(test_image)
            images.append(test_image_array.tolist())

        scoring_payload = {'values': images}

        TestAIOpenScaleClient.scoring_records = len(images) * 3

        for i in range(0, self.scoring_records):
            scores = self.wml_client.deployments.score(scoring_url=scoring_endpoint, payload=scoring_payload)
            self.assertIsNotNone(scores)

        print("Scoring result: {}".format(scores))

        wait_for_payload_propagation(is_wml_engine=False)

    def test_13_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()

        assert_payload_logging_unstructured_data(subscription=self.subscription)

    def test_14_stats_on_performance_monitoring_table(self):
        if "ICP" in get_env():
            self.skipTest("Performance monitoring is not working on ICP with WML scoring.")

        self.subscription.performance_monitoring.print_table_schema()
        self.subscription.performance_monitoring.show_table()
        self.subscription.performance_monitoring.describe_table()

        performance_table_pandas = self.subscription.performance_monitoring.get_table_content()
        assert_performance_monitoring_pandas_table_content(pandas_table_content=performance_table_pandas)

        performance_table_python = self.subscription.performance_monitoring.get_table_content(format='python')
        assert_performance_monitoring_python_table_content(python_table_content=performance_table_python)

    def test_15_enable_quality_monitoring(self):
        self.subscription.quality_monitoring.enable(threshold=0.7, min_records=10)

        details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        assert_quality_monitoring_configuration(quality_monitoring_details=details)

    def test_16_feedback_logging(self):
        TestAIOpenScaleClient.feedback_records = 0
        for file in glob.glob("datasets/dogs-vs-cats/feedback-data/*.jpg"):
            test_image = load_img(file, target_size=(150, 150))
            test_image_array = img_to_array(test_image)
            test_image_list = test_image_array.tolist()

            image_label = 0
            if "dog" in file:
                image_label = 1

            feedback_data = [[test_image_list, image_label]]

            self.subscription.feedback_logging.store(feedback_data=feedback_data)

            TestAIOpenScaleClient.feedback_records += 1

        print("Waiting 30 seconds for records.")
        time.sleep(30)

    def test_17_feedback_logging_deprecated(self):
        feedback_payload = ""
        for file in glob.glob("datasets/dogs-vs-cats/feedback-data/*.jpg"):
            test_image = load_img(file, target_size=(150, 150))
            test_image_array = img_to_array(test_image)
            feedback_payload += str(test_image_array.tolist())
            if "dog" in file:
                feedback_payload += ";[1]\n"
            else:
                feedback_payload += ";[0]\n"

            TestAIOpenScaleClient.feedback_records += 1

        self.subscription.feedback_logging.store(feedback_data=feedback_payload, feedback_format=FeedbackFormat.CSV,
                                                 data_header=False, data_delimiter=';')

        print("Waiting 30 seconds for records.")

        time.sleep(30)

    def test_18_stats_on_feedback_logging(self):
        self.subscription.feedback_logging.show_table()
        assert_feedback_logging_unstructured_data(subscription=self.subscription, feedback_records=self.feedback_records)

    def test_19_run_quality_monitoring(self):
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

    def test_20_get_metrics(self):
        print("Old quality metrics:\n{}".format(self.subscription.get_deployment_metrics(metric_type="quality")))
        print("New quality metrics: ")
        print(TestAIOpenScaleClient.subscription.quality_monitoring.get_metrics(deployment_uid=""))

        self.assertGreater(len(TestAIOpenScaleClient.subscription.quality_monitoring.get_metrics(deployment_uid="")), 0)
        print(TestAIOpenScaleClient.subscription.quality_monitoring.get_metrics(deployment_uid="", format="samples"))

    def test_21_stats_on_quality_monitoring_table(self):
        self.subscription.quality_monitoring.print_table_schema()
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_table(limit=None)
        self.subscription.quality_monitoring.describe_table()

        quality_monitoring_table = self.subscription.quality_monitoring.get_table_content()
        assert_quality_monitoring_pandas_table_content(pandas_table_content=quality_monitoring_table)

        quality_metrics = self.subscription.quality_monitoring.get_table_content(format='python')
        assert_quality_monitoring_python_table_content(python_table_content=quality_metrics)

    def test_22_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_23_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()

        clean_wml_instance(model_id=cls.model_uid, deployment_id=cls.deployment_uid)


if __name__ == '__main__':
    unittest.main()
