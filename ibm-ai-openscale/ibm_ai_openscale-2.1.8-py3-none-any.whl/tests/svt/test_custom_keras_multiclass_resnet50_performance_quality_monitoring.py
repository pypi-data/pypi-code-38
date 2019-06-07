# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import numpy as np
import requests
from PIL import Image
from keras.applications import imagenet_utils
from keras.preprocessing.image import img_to_array

from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes.payload_record import PayloadRecord


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
    scoring_records = None
    start_date = datetime.utcnow().isoformat() + "Z"

    test_uid = str(uuid.uuid4())

    # Custom deployment configuration
    credentials = {
        "url": "http://169.63.194.147:31520",
        "username": "xxx",
        "password": "yyy"
    }

    image_path = os.path.join(os.getcwd(), 'datasets', 'images', 'labrador.jpg')

    def score(self, subscription_details):
        image = Image.open(self.image_path)

        if image.mode is not "RGB":
            image = image.convert("RGB")

        image = image.resize((224, 224))
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        image = imagenet_utils.preprocess_input(image)
        image_list = image.tolist()

        print('Size of image list', len(image_list), len(image_list[0]))
        print('Image list', image_list)

        payload = {'values': [image_list, image_list]}
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer xxx'}
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

        response = requests.post(scoring_url, json=payload, headers=header)
        print('scoring', response.json())

        return payload, response.json(), 25

    def prepare_feedback_record(self, image_path, label):
        image = Image.open(image_path)

        if image.mode is not "RGB":
            image = image.convert("RGB")

        image = image.resize((224, 224))
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        image = imagenet_utils.preprocess_input(image)
        image_list = image.tolist()

        return [image_list, label]


    @classmethod
    def setUpClass(cls):
        try:
            requests.get(url="{}/v1/deployments".format(cls.credentials['url']), timeout=10)
        except:
            raise unittest.SkipTest("Custom app is not available.")

        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        if "ICP" in get_env():
            cls.ai_client = APIClient4ICP(cls.aios_credentials)
        else:
            cls.ai_client = APIClient(cls.aios_credentials)

        prepare_env(cls.ai_client)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()

    def test_01_setup_data_mart(self):
        self.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_02_bind_custom(self):
        TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("My Custom deployment", CustomMachineLearningInstance(self.credentials))
        print("Binding uid: {}".format(self.binding_uid))
        self.assertIsNotNone(self.binding_uid)

    def test_03_get_binding_details(self):
        binding_details = self.ai_client.data_mart.bindings.get_details()
        print("Binding details: {}".format(binding_details))
        self.assertIsNotNone(binding_details)

    def test_04_get_deployments(self):
        print('Available deployments: {}'.format(self.ai_client.data_mart.bindings.list_assets()))
        self.ai_client.data_mart.bindings.list_assets()
        print(self.ai_client.data_mart.bindings.get_asset_details())

    def test_05_subscribe_custom(self):
        from ibm_ai_openscale.supporting_classes.enums import InputDataType
        subscription = self.ai_client.data_mart.subscriptions.add(
            CustomMachineLearningAsset(
                source_uid='resnet50',
                binding_uid=self.binding_uid,
                input_data_type=InputDataType.UNSTRUCTURED_IMAGE,
                label_column='target',
                prediction_column='prediction',
                probability_column='prediction_probability'),
            deployment_uids=['resnet50'])
        TestAIOpenScaleClient.subscription_uid = subscription.uid
        print("Subscription id: {}".format(self.subscription_uid))
        self.assertIsNotNone(self.subscription_uid)

    def test_06_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)
        print(self.subscription.get_details())

    def test_07_list_deployments(self):
        print("Listing deployments:\n")
        self.subscription.list_deployments()

    def test_08_check_default_monitors_enablement(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details, payload=True, performance=True)

    def test_09_get_payload_logging_details(self):
        payload_logging_details = self.subscription.payload_logging.get_details()
        assert_payload_logging_configuration(payload_logging_details=payload_logging_details, dynamic_schema_update=False)

    def test_10_get_performance_monitoring_details(self):
        performance_monitoring_details = self.subscription.performance_monitoring.get_details()
        assert_performance_monitoring_configuration(performance_monitoring_details=performance_monitoring_details)

    def test_12_score_model_and_log_payload(self):

        request, response, response_time = self.score(self.subscription.get_details())
        print('response', response)

        records_list = []

        TestAIOpenScaleClient.scoring_records = 2
        for i in range(0, self.scoring_records):
            records_list.append(PayloadRecord(request=request, response=response, response_time=response_time))

        self.subscription.payload_logging.store(records=records_list)
        print("Waiting 30 seconds for propagation...")
        time.sleep(30)

    def test_13_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        assert_payload_logging_unstructured_data(subscription=self.subscription, scoring_records=self.scoring_records*2)
        self.subscription.payload_logging.show_table()

    def test_14_stats_on_performance_monitoring_table(self):
        self.subscription.performance_monitoring.print_table_schema()
        self.subscription.performance_monitoring.show_table()
        self.subscription.performance_monitoring.describe_table()

        performance_table_pandas = self.subscription.performance_monitoring.get_table_content()
        assert_performance_monitoring_pandas_table_content(pandas_table_content=performance_table_pandas)

        performance_table_python = self.subscription.performance_monitoring.get_table_content(format='python')
        assert_performance_monitoring_python_table_content(python_table_content=performance_table_python)

    def test_15_enable_quality_monitoring(self):
        self.subscription.quality_monitoring.enable(threshold=0.7, min_records=5)
        details = self.subscription.quality_monitoring.get_details()
        self.assertTrue('True' in str(details))

    def test_16_store_feedback_records(self):
        feedback_records = []
        feedback_record = self.prepare_feedback_record(self.image_path, 'Labrador_retriever')

        print('feedback_record', feedback_record)

        for i in range(0, 2):
            feedback_records.append(feedback_record)

        for j in range(0, 5):
            TestAIOpenScaleClient.subscription.feedback_logging.store(feedback_data=feedback_records)
        time.sleep(10)

    def test_17_stats_on_feedback_logging(self):
        TestAIOpenScaleClient.subscription.feedback_logging.show_table()
        TestAIOpenScaleClient.subscription.feedback_logging.print_table_schema()
        assert_feedback_logging_unstructured_data(subscription=TestAIOpenScaleClient.subscription, feedback_records=10)

    def test_18_run_quality_monitoring(self):
        run_details = self.subscription.quality_monitoring.run(background_mode=False)
        assert_quality_run(run_details=run_details)
        status = run_details['status']
        self.assertIn('completed', status)

    def test_19_stats_on_quality_monitoring_table(self):
        self.subscription.quality_monitoring.print_table_schema()
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_table(limit=None)
        self.subscription.quality_monitoring.describe_table()
        self.subscription.quality_monitoring.get_table_content()
        quality_metrics = self.subscription.quality_monitoring.get_table_content(format='python')
        self.assertGreater(len(quality_metrics['values']), 0)
    #
    # def test_20_enable_explainablity(self):
    #     TestAIOpenScaleClient.subscription.explainability.enable()

    # def test_21_run_explanation(self):
    #     transaction_id = TestAIOpenScaleClient.subscription.payload_logging.get_table_content(limit=1)['scoring_id'].values[0]
    #     print(transaction_id)
    #
    #     explain_run = TestAIOpenScaleClient.subscription.explainability.run(transaction_id=transaction_id, background_mode=False)
    #     print('explain run', explain_run)

    def test_30_disable_performance_monitoring(self):
        TestAIOpenScaleClient.subscription.performance_monitoring.disable()
        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        print("Subscription details after disabling performance monitoring:\n{}".format(subscription_details))

    def test_31_disable_payload_logging(self):
        self.subscription.payload_logging.disable()

    def test_32_get_metrics(self):
        print("Old metrics:")
        print(self.ai_client.data_mart.get_deployment_metrics())
        print(self.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(self.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(self.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))

    def test_33_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_34_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)


if __name__ == '__main__':
    unittest.main()
