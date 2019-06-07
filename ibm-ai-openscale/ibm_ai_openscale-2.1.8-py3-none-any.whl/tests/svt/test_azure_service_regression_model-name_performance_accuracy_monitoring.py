# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import pandas as pd
import requests

from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes.data_distribution_agg import Agg
from ibm_ai_openscale.supporting_classes import PayloadRecord
from ibm_ai_openscale.supporting_classes.enums import InputDataType, ProblemType, FeedbackFormat
from preparation_and_cleaning import *


@unittest.skip("Not implemented.")
class TestAIOpenScaleClient(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    binding_uid = None
    scoring_url = None
    labels = None
    ai_client = None
    wml_client = None
    subscription = None
    test_uid = str(uuid.uuid4())
    source_uid = None
    transaction_id = None
    training_data_statistics = None
    start_date = datetime.utcnow().isoformat() + 'Z'
    scoring_records = None
    feedback_records = None
    monitor_uid = None


    # TODO -> update azure service credentials
    # Model training data
    data_df = pd.read_csv()

    # TODO -> update azure service credentials
    # Azure Service configuration
    credentials = {

    }

    # TODO -> update scoring method with correct payload
    # Scoring method
    def score(self, subscription_details):
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

        data = {
            "Inputs": {
                "input1":
                    [
                        {
                            'GENDER': "F",
                            'AGE': "27",
                            'MARITAL_STATUS': "Single",
                            'PROFESSION': "Professional",
                            'PRODUCT_LINE': "Personal Accessories",
                        }
                    ],
            },
            "GlobalParameters": {
            }
        }

        body = str.encode(json.dumps(data))

        token = subscription_details['entity']['deployments'][0]['scoring_endpoint']['credentials']['token']
        headers = subscription_details['entity']['deployments'][0]['scoring_endpoint']['request_headers']
        headers['Authorization'] = ('Bearer ' + token)

        start_time = time.time()
        response = requests.post(url=scoring_url, data=body, headers=headers)
        response_time = time.time() - start_time
        result = response.json()

        request = data
        response = result

        print("Request: {}".format(data))
        print("Response: {}".format(response))
        return request, response, response_time

    @classmethod
    def setUpClass(cls):
        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        if "ICP" in get_env():
            cls.ai_client = APIClient4ICP(cls.aios_credentials)
        else:
            cls.ai_client = APIClient(cls.aios_credentials)

        prepare_env(cls.ai_client)

    def test_01_setup_data_mart(self):
        self.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)
        details = TestAIOpenScaleClient.ai_client.data_mart.get_details()
        assert_datamart_details(details, schema=self.schema, state='active')

    def test_02_bind_azure(self):

        # TODO -> Change Azure engine in binding

        TestAIOpenScaleClient.binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.add("Azure ml engine", AzureMachineLearningInstance(self.credentials))
        print("Binding uid: {}".format(self.binding_uid))

    def test_03_get_binding_details(self):
        print("Binding details: {}".format(self.ai_client.data_mart.bindings.get_details(self.binding_uid)))
        self.ai_client.data_mart.bindings.list()

    def test_04_get_assets(self):
        asset_details = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_asset_details()
        print('Assets details: ' + str(asset_details))

        for detail in asset_details:

            # TODO -> provide valid model name

            if 'ProductLineAgeRe.2018.10.22.7.33.27.127' in detail['name']:
                TestAIOpenScaleClient.source_uid = detail['source_uid']

        self.assertIsNotNone(TestAIOpenScaleClient.source_uid)

    def test_05_subscribe_azure_asset(self):

        # TODO -> update subscription configuration correct type of asset

        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            AzureMachineLearningAsset(source_uid=TestAIOpenScaleClient.source_uid,
                                      binding_uid=TestAIOpenScaleClient.binding_uid,
                                      input_data_type=InputDataType.STRUCTURED,
                                      problem_type=ProblemType.REGRESSION,
                                      label_column='AGE',
                                      prediction_column='Scored Labels'
                                      )
        )

        TestAIOpenScaleClient.subscription_uid = subscription.uid
        print('Subscription details: {}'.format(subscription.get_details()))

    def test_06_get_subscription_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.subscription_uid)
        details = self.subscription.get_details()

        assert_subscription_details(subscription_details=details, no_deployments=1, text_included='azureml', enabled_monitors=['payload_logging', 'performance_monitoring'])

    def test_07_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_08_get_payload_logging_details(self):
        payload_logging_details = self.subscription.payload_logging.get_details()
        assert_payload_logging_configuration(payload_logging_details=payload_logging_details, dynamic_schema_update=False)

    def test_09_get_performance_monitoring_details(self):
        performance_monitoring_details = self.subscription.performance_monitoring.get_details()
        assert_performance_monitoring_configuration(performance_monitoring_details=performance_monitoring_details)

    def test_10_score_model_and_log_payload(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        request, response, response_time = self.score(subscription_details)

        records_list = []

        TestAIOpenScaleClient.scoring_records = 5
        for i in range(0, self.scoring_records):
            records_list.append(PayloadRecord(request=request, response=response, response_time=int(response_time)))

        TestAIOpenScaleClient.subscription.payload_logging.store(records=records_list)

        wait_for_payload_propagation(is_wml_engine=False)

    def test_11_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        self.subscription.payload_logging.show_table()
        self.subscription.payload_logging.describe_table()

        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content, scoring_records=self.scoring_records)

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')

        # TODO -> check if columns in payload table are correct
        assert_payload_logging_python_table_content(python_table_content=python_table_content, fields=['Scored Labels'])

    def test_12_stats_on_performance_monitoring_table(self):
        self.subscription.performance_monitoring.print_table_schema()
        self.subscription.performance_monitoring.show_table()
        self.subscription.performance_monitoring.describe_table()

        performance_table_pandas = self.subscription.performance_monitoring.get_table_content()
        assert_performance_monitoring_pandas_table_content(pandas_table_content=performance_table_pandas)

        performance_table_python = self.subscription.performance_monitoring.get_table_content(format='python')
        assert_performance_monitoring_python_table_content(python_table_content=performance_table_python)

    def test_13_payload_logging_data_distribution(self):

        # TODO -> update payload data distribution

        end_date = datetime.utcnow().isoformat() + "Z"
        data_distribution_run = self.subscription.payload_logging.data_distribution.run(
            start_date=TestAIOpenScaleClient.start_date,
            end_date=end_date,
            group=['AGE', 'MARITAL_STATUS'],
            background_mode=False)

        data_distribution_run_id = data_distribution_run['id']
        data_distribution = self.subscription.payload_logging.data_distribution.get_run_result(run_id=data_distribution_run_id)

        print('Payload data distribution')
        print(data_distribution)

        self.assertEqual(data_distribution.shape[0], 1)
        self.assertEqual(data_distribution.shape[1], 3)
        data_columns = data_distribution.columns.values
        self.assertIn("AGE", data_columns)
        self.assertIn("MARITAL_STATUS", data_columns)
        self.assertIn("count", data_columns)

    def test_14_setup_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.enable(threshold=0.8, min_records=5)

    def test_15_get_quality_monitoring_details(self):
        details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        assert_quality_monitoring_configuration(quality_monitoring_details=details)

    def test_16_send_feedback_data(self):

        # TODO -> Update feedback data

        TestAIOpenScaleClient.feedback_records = 50

        training_data = pd.read_csv('datasets/GoSales/GoSales_Tx_NaiveBayes.csv')

        self.subscription.feedback_logging.store(
            feedback_data=training_data.sample(n=self.feedback_records).to_csv(index=False),
            feedback_format=FeedbackFormat.CSV,
            data_header=True,
            data_delimiter=',')

        print("Waiting 30 seconds for propagation.")
        time.sleep(30)

    def test_17_stats_on_feedback_logging_table(self):
        self.subscription.feedback_logging.show_table()
        self.subscription.feedback_logging.print_table_schema()
        self.subscription.feedback_logging.describe_table()

        feedback_pd = self.subscription.feedback_logging.get_table_content(format='pandas')
        assert_feedback_pandas_table_content(pandas_table_content=feedback_pd, feedback_records=self.feedback_records)

    def test_18_feedback_logging_data_distribution(self):

        # TODO -> update feedback data distribution

        feedback_distribution_run = TestAIOpenScaleClient.subscription.feedback_logging.data_distribution.run(
            group=['PROFESSION'],
            agg=[Agg.count()])
        feedback_distribution_run_id = feedback_distribution_run['id']
        feedback_distribution = self.subscription.feedback_logging.data_distribution.get_run_result(run_id=feedback_distribution_run_id)

        print("Feedback data distribution:")
        print(feedback_distribution)

        self.assertGreater(feedback_distribution.shape[0], 5)
        self.assertEqual(feedback_distribution.shape[1], 2)

    def test_19_run_quality_monitor(self):
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
            self.assertNotIn('failed', status, msg="Quality run failed.")

        self.assertTrue('completed' in status)

    def test_20_stats_on_quality_monitoring_table(self):
        self.subscription.quality_monitoring.print_table_schema()
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_table(limit=None)
        self.subscription.quality_monitoring.describe_table()

        quality_monitoring_table = self.subscription.quality_monitoring.get_table_content()
        assert_quality_monitoring_pandas_table_content(pandas_table_content=quality_monitoring_table)

        quality_metrics = self.subscription.quality_monitoring.get_table_content(format='python')
        assert_quality_monitoring_python_table_content(python_table_content=quality_metrics)

    def test_21_get_ootb_metrics(self):
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
                self.assertEqual(metric['value'], metrics[metric['id']], msg="metric {} has different value in ootb api".format(metric['id']))
                if 'lower_limit' in metric.keys():
                    self.assertEqual(metric['lower_limit'], metrics['threshold'], msg="lower_limit is not the same as threshold!")

        print(self.subscription.quality_monitoring.get_metrics(format="samples"))

    def test_22_define_custom_monitor(self):
        from ibm_ai_openscale.supporting_classes import Metric, Tag

        metrics = [Metric(name='mean_absolute_error', lower_limit_default=0.5),
                   Metric(name='mean_squared_log_error')]
        tags = [Tag(name='region', description='tag description', required=True),
                Tag(name='notrequired', description='tag description not', required=False)]

        custom_monitor = self.ai_client.data_mart.monitors.add(name='custom monitor name', metrics=metrics, tags=tags)
        print('Custom monitor definition details:\n{}'.format(custom_monitor))

        TestAIOpenScaleClient.monitor_uid = self.ai_client.data_mart.monitors.get_uids(name='custom monitor name')[0]
        print('Custom monitor uid: {}'.format(TestAIOpenScaleClient.monitor_uid))

        self.assertIsNotNone(custom_monitor)
        self.assertIsNotNone(TestAIOpenScaleClient.monitor_uid)

    def test_23_list_custom_monitors(self):
        self.ai_client.data_mart.monitors.list()

    def test_24_get_custom_monitor_details(self):
        custom_monitor = self.ai_client.data_mart.monitors.get_details(TestAIOpenScaleClient.monitor_uid)
        print('Custom monitor definition details:\n{}'.format(custom_monitor))

    def test_25_enable_monitoring(self):
        from ibm_ai_openscale.supporting_classes import Threshold

        thresholds = [Threshold(metric_uid='mean_absolute_error', lower_limit=0.3)]
        self.subscription.monitoring.enable(TestAIOpenScaleClient.monitor_uid, thresholds=thresholds)

        for configuration in TestAIOpenScaleClient.subscription.get_details()['entity']['configurations']:
            if configuration['type'] == TestAIOpenScaleClient.monitor_uid:
                self.assertEqual(configuration['enabled'], True)

    def test_25_get_monitoring_details(self):
        details = TestAIOpenScaleClient.subscription.monitoring.get_details(monitor_uid=self.monitor_uid)
        print('custom monitoring', details)

        self.assertIsNotNone(details)

    def test_26_disable_all_monitors(self):
        self.subscription.payload_logging.disable()
        self.subscription.performance_monitoring.disable()
        self.subscription.quality_monitoring.disable()

        subscription_details = self.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details)

    def test_27_unsubscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(TestAIOpenScaleClient.subscription.uid)

    def test_28_unbind(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.delete(TestAIOpenScaleClient.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
