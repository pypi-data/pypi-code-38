# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import pickle
import pandas as pd

from keras.preprocessing.sequence import pad_sequences

from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType, FeedbackFormat


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
    test_uid = str(uuid.uuid4())
    scoring_records = None
    feedback_records = None

    model_path = os.path.join(os.getcwd(), 'artifacts', 'poland_house_prices', 'poland_house_prices.h5.tgz')

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

        with open('artifacts/poland_house_prices/poland_prices_tokenizer.pickle', 'rb') as handle:
            cls.tokenizer = pickle.load(handle)

        with open('artifacts/poland_house_prices/poland_prices_scaler.pickle', 'rb') as handle:
            cls.scaler = pickle.load(handle)

    def test_01_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_02_data_mart_get_details(self):
        details = TestAIOpenScaleClient.ai_client.data_mart.get_details()
        assert_datamart_details(details=details, schema=self.schema)

    def test_03_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud",WatsonMachineLearningInstance(self.wml_credentials))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_05_prepare_deployment(self):
        model_name = "AIOS Keras Poland house prices model"
        deployment_name = "AIOS Poland house prices deployment"

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
                problem_type=ProblemType.REGRESSION,
                input_data_type=InputDataType.UNSTRUCTURED_TEXT,
                label_column='price'
            )
        )
        TestAIOpenScaleClient.aios_model_uid = subscription.uid

    def test_07_get_subscription(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)

        subscription_details = self.subscription.get_details()
        print("Subscription details:\n{}".format(subscription_details))

    def test_08_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_09_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details, payload=True, performance=True)

    def test_10_get_payload_logging_details(self):
        payload_logging_details = self.subscription.payload_logging.get_details()
        assert_payload_logging_configuration(payload_logging_details=payload_logging_details)

    def test_11_get_performance_monitor_details(self):
        performance_monitoring_details = self.subscription.performance_monitoring.get_details()
        assert_performance_monitoring_configuration(performance_monitoring_details=performance_monitoring_details)

    def test_12_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        messages = [
            "Poznań, Rynek Wildecki, wielkopolskie, Powierzchnia w m2: 44.82, Liczba pokoi: 2, Piętro: 1, Typ zabudowy: kamienica, Liczba pięter w budynku: 6, Nazwa inwestycji: Rynek Wildecki 3",
            "Poznań, Rynek Wildecki, wielkopolskie, Powierzchnia w m2: 34.84, Liczba pokoi: 1, Piętro: 5,  Typ zabudowy: kamienica, Liczba pięter w budynku: 6, Nazwa inwestycji: Rynek Wildecki 3",
            "Łódź, Bałuty, łódzkie, Powierzchnia w m2: 51.96, Liczba pokoi: 2, Piętro: parter, Typ zabudowy: blok, Liczba pięter w budynku: 4, Nazwa inwestycji: Villa Romanów",
            "Kraków, Prokocim, małopolskie, Powierzchnia w m2: 55.14, Liczba pokoi: 3, Piętro: 2, Typ zabudowy: blok, Liczba pięter w budynku: 3, Miejsce parkingowe: przynależne na ulicy",
            "Wrocław, Wojszyce, dolnośląskie, Powierzchnia w m2: 46.48, Liczba pokoi: 2, Piętro: parter, Typ zabudowy: blok, Liczba pięter w budynku: 2, Nazwa inwestycji: Małe Wojszyce",
            "Wrocław, Krzyki, dolnośląskie, Powierzchnia w m2: 66.59, Liczba pokoi: 3, Piętro: 6, Typ zabudowy: blok, Liczba pięter w budynku: 8, Nazwa inwestycji: Kamienna 145",
            "Warszawa, Gocław, mazowieckie, Powierzchnia w m2: 78.49, Liczba pokoi: 4, Piętro: 15, Liczba pięter w budynku: 17, Nazwa inwestycji: Korona Pragi, ID Inwestycji: 65298180",
            "Warszawa, Służewiec, mazowieckie, Powierzchnia w m2: 61.36, Liczba pokoi: 3, Piętro: 6, Typ zabudowy: blok, Liczba pięter w budynku: 9, Nazwa inwestycji: Osiedle Krzemowe",
            "Wrocław, Klecina, dolnośląskie, Powierzchnia w m2: 59.62, Liczba pokoi: 3, Piętro: parter, Typ zabudowy: blok, Liczba pięter w budynku: 3, Nazwa inwestycji: Między Parkami",
            "Warszawa, Wola, mazowieckie, Powierzchnia w m2: 74.03, Liczba pokoi: 4, Piętro: 3, Typ zabudowy: blok, Liczba pięter w budynku: 7, Nazwa inwestycji: Osiedle Na Woli"
            ]
        tokenized_messages = self.tokenizer.texts_to_sequences(messages)
        tokenized_messages = pad_sequences(tokenized_messages, padding='post', maxlen=28)
        scoring_payload = {'values': tokenized_messages.tolist()}

        TestAIOpenScaleClient.scoring_records = len(messages)

        scores = self.wml_client.deployments.score(scoring_url=scoring_endpoint, payload=scoring_payload)
        self.assertIsNotNone(scores)

        print(scores)
        wait_for_payload_propagation(is_wml_engine=False)

    def test_13_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        assert_payload_logging_unstructured_data(subscription=self.subscription, scoring_records=self.scoring_records)

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
        print(self.subscription.get_details())
        feedback_data = pd.read_csv('datasets/poland_house_prices/poland_house_prices_feedback.txt', names=["text", "price"], sep=";")
        for index, row in feedback_data.iterrows():
            tokenized_messages = self.tokenizer.texts_to_sequences([row['text']])
            tokenized_messages = pad_sequences(tokenized_messages, padding='post', maxlen=28).tolist()
            target_field = self.scaler.transform(row['price']).tolist()[0][0]
            feedback_data_row = [[tokenized_messages[0], target_field]]
            self.subscription.feedback_logging.store(feedback_data=feedback_data_row, feedback_format=FeedbackFormat.WML, fields=['scoring_input', 'target'])

        print("Waiting 20 seconds for records.")
        time.sleep(20)
        TestAIOpenScaleClient.feedback_records = 40

    def test_17_stats_on_feedback_logging(self):
        self.subscription.feedback_logging.show_table()
        assert_feedback_logging_unstructured_data(subscription=self.subscription, feedback_records=self.feedback_records)

    def test_18_run_quality_monitoring(self):
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
            print("Status: {}\nRun details: {}".format(status, run_details))
            self.assertNotEqual('failed', status)

        self.assertEqual('completed', status)

    def test_19_stats_on_quality_monitoring_table(self):
        self.subscription.quality_monitoring.print_table_schema()
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_table(limit=None)
        self.subscription.quality_monitoring.describe_table()

        quality_monitoring_table = self.subscription.quality_monitoring.get_table_content()
        assert_quality_monitoring_pandas_table_content(pandas_table_content=quality_monitoring_table)

        quality_metrics = self.subscription.quality_monitoring.get_table_content(format='python')
        assert_quality_monitoring_python_table_content(python_table_content=quality_metrics)

    def test_20_get_metrics(self):
        print("Old metrics:")
        print(self.ai_client.data_mart.get_deployment_metrics())
        print(self.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(self.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(self.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))

        ### REGRESSION CHECK

        metrics = {
            'threshold': None,
            'explained_variance': None,
            'root_mean_squared_error': None,
            'mean_absolute_error': None,
            'mean_squared_error': None,
            'r2': None
        }

        quality_metrics = self.ai_client.data_mart.get_deployment_metrics(metric_type='quality')
        print("Old quality metric:\n{}".format(quality_metrics))

        for metric in quality_metrics['deployment_metrics'][0]['metrics'][0]['value']['metrics']:
            if metric['name'] in metrics.keys():
                metrics[metric['name']] = metric['value']

        metrics['threshold'] = quality_metrics['deployment_metrics'][0]['metrics'][0]['value']['threshold']

        ootb_quality_metrics = self.subscription.quality_monitoring.get_metrics()
        print("New quality metrics:\n{}".format(ootb_quality_metrics))

        for metric in ootb_quality_metrics[0]['metrics']:
            if metric['id'] in metrics.keys():
                if metrics[metric['id']] is not float:
                    break
                self.assertEqual(metric['value'], metrics[metric['id']], msg="metric {} has different value in ootb api".format(metric['id']))
                if 'lower_limit' in metric.keys():
                    self.assertEqual(metric['lower_limit'], metrics['threshold'], msg="lower_limit is not the same as threshold!")

        print(self.subscription.quality_monitoring.get_metrics(format="samples"))

    def test_21_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_22_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()

        clean_wml_instance(model_id=cls.model_uid, deployment_id=cls.deployment_uid)


if __name__ == '__main__':
    unittest.main()
