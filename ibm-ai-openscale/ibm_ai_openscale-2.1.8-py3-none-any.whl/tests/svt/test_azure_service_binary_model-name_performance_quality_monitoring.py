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
    scoring_records = None
    feedback_records = None
    start_date = datetime.utcnow().isoformat() + "Z"

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
                            'CheckingStatus': "0_to_200",
                            'LoanDuration': "31",
                            'CreditHistory': "credits_paid_to_date",
                            'LoanPurpose': "other",
                            'LoanAmount': "1889",
                            'ExistingSavings': "100_to_500",
                            'EmploymentDuration': "less_1",
                            'InstallmentPercent': "3",
                            'Sex': "female",
                            'OthersOnLoan': "none",
                            'CurrentResidenceDuration': "3",
                            'OwnsProperty': "savings_insurance",
                            'Age': "32",
                            'InstallmentPlans': "none",
                            'Housing': "own",
                            'ExistingCreditsCount': "1",
                            'Job': "skilled",
                            'Dependents': "1",
                            'Telephone': "none",
                            'ForeignWorker': "yes",
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
        print('--> Azure\nScoring payload: {}\nScoring result: {}\nResponse time: {}'.format(data, result, response_time))

        return data, result, response_time

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
        print('Binding details: {}'.format(TestAIOpenScaleClient.ai_client.data_mart.bindings.get_details(TestAIOpenScaleClient.binding_uid)))
        self.ai_client.data_mart.bindings.list()

    def test_04_get_assets(self):
        assets_uids = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_asset_uids()
        self.assertGreater(len(assets_uids), 1)
        print('Assets uids: ' + str(assets_uids))

        TestAIOpenScaleClient.ai_client.data_mart.bindings.list_assets()
        asset_details = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_asset_details(binding_uid=TestAIOpenScaleClient.binding_uid)
        print('Assets details: ' + str(asset_details))

        for detail in asset_details:

            # TODO -> provide valid model name

            if 'GermanCreditRisk.2019.1.9.10.41.58.611' in detail['name']:
                TestAIOpenScaleClient.source_uid = detail['source_uid']

        print("Source uid: {}".format(self.source_uid))

        self.assertIsNotNone(TestAIOpenScaleClient.source_uid)

    def test_05_subscribe_azure_asset(self):

        # TODO -> update subscription configuration correct type of asset

        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            AzureMachineLearningAsset(
                source_uid=TestAIOpenScaleClient.source_uid,
                binding_uid=TestAIOpenScaleClient.binding_uid,
                input_data_type=InputDataType.STRUCTURED,
                problem_type=ProblemType.BINARY_CLASSIFICATION,
                probability_column='',
                label_column='',
                prediction_column='',
                feature_columns=[],
                categorical_columns=[]
            )
        )

        TestAIOpenScaleClient.subscription_uid = subscription.uid

    def test_06_get_subscription_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.subscription_uid)
        details = self.subscription.get_details()

        assert_subscription_details(subscription_details=details, no_deployments=1, text_included='azureml', enabled_monitors=['payload_logging', 'performance_monitoring'])

    def test_07_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_08_check_default_monitors_enablement(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details, payload=True, performance=True)

    def test_09_get_payload_logging_details(self):
        payload_logging_details = self.subscription.payload_logging.get_details()
        assert_payload_logging_configuration(payload_logging_details=payload_logging_details, dynamic_schema_update=False)

    def test_10_get_performance_monitoring_details(self):
        performance_monitoring_details = self.subscription.performance_monitoring.get_details()
        assert_performance_monitoring_configuration(performance_monitoring_details=performance_monitoring_details)

    def test_11_score_model_and_log_payload(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        request, response, response_time = self.score(subscription_details)
        records_list = []
        import random
        TestAIOpenScaleClient.scoring_records = 10
        for i in range(0, self.scoring_records):
            records_list.append(PayloadRecord(request=request, response=response, response_time=random.randint(0, 10)))

        TestAIOpenScaleClient.subscription.payload_logging.store(records=records_list)

        wait_for_payload_propagation(is_wml_engine=False)

    def test_12_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        self.subscription.payload_logging.show_table()
        self.subscription.payload_logging.describe_table()

        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content, scoring_records=self.scoring_records)

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')

        # TODO -> check if columns in payload table are correct
        assert_payload_logging_python_table_content(python_table_content=python_table_content, fields=['Scored Probabilities', 'Scored Labels'])

        print('subscription details', TestAIOpenScaleClient.subscription.get_details())

    def test_13_payload_logging_data_distribution(self):

        # TODO -> update payload data distribution

        end_date = datetime.utcnow().isoformat() + "Z"
        data_distribution_run = TestAIOpenScaleClient.subscription.payload_logging.data_distribution.run(
            start_date=self.start_date,
            end_date=end_date,
            group=['Scored Labels', 'Age', 'Sex'],
            background_mode=False)

        run_id = data_distribution_run['id']
        data_distribution = self.subscription.payload_logging.data_distribution.get_run_result(run_id=run_id)
        print('Payload data distribution')
        print(data_distribution)

        self.assertTrue("32" in str(data_distribution))

    def test_14_stats_on_performance_monitoring_table(self):
        self.subscription.performance_monitoring.print_table_schema()
        self.subscription.performance_monitoring.show_table()
        self.subscription.performance_monitoring.describe_table()

        performance_table_pandas = self.subscription.performance_monitoring.get_table_content()
        assert_performance_monitoring_pandas_table_content(pandas_table_content=performance_table_pandas)

        performance_table_python = self.subscription.performance_monitoring.get_table_content(format='python')
        assert_performance_monitoring_python_table_content(python_table_content=performance_table_python)

    def test_15_setup_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.enable(threshold=0.8, min_records=5)

    def test_16_get_quality_monitoring_details(self):
        details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        assert_quality_monitoring_configuration(quality_monitoring_details=details)

    def test_17_send_feedback_data(self):

        # TODO -> Update feedback data

        print(self.subscription.get_details())
        TestAIOpenScaleClient.feedback_records = 40

        feedback_data = pd.read_csv('datasets/German_credit_risk/credit_risk_training.csv', sep=",")

        self.subscription.feedback_logging.store(
            feedback_data=feedback_data.sample(n=self.feedback_records).to_csv(index=False),
            feedback_format=FeedbackFormat.CSV,
            data_header=True,
            data_delimiter=',')

        print("Waiting 30 seconds for propagation.")
        time.sleep(30)

    def test_18_stats_on_feedback_logging_table(self):
        self.subscription.feedback_logging.show_table()
        self.subscription.feedback_logging.print_table_schema()
        self.subscription.feedback_logging.describe_table()

        feedback_pd = self.subscription.feedback_logging.get_table_content(format='pandas')
        assert_feedback_pandas_table_content(pandas_table_content=feedback_pd, feedback_records=self.feedback_records)

    def test_19_feedback_logging_data_distribution(self):

        # TODO -> update feedback data distribution

        end_date = datetime.utcnow().isoformat() + "Z"
        feedback_distribution = TestAIOpenScaleClient.subscription.feedback_logging.data_distribution.run(
            start_date=TestAIOpenScaleClient.start_date,
            end_date=end_date,
            group=['LoanPurpose'],
            agg=['LoanDuration:avg', 'LoanAmount:avg'],
            background_mode=True)
        distribution_run_id = feedback_distribution['id']
        print("Feedback data distribution run:")
        print(feedback_distribution)

        status = feedback_distribution['status']
        while status == 'initializing' or status == 'running':
            run_details = self.subscription.feedback_logging.data_distribution.get_run_details(run_id=distribution_run_id)
            status = run_details['status']
            print("Distribution run status: {}".format(status))
            time.sleep(10)

        run_result = self.subscription.feedback_logging.data_distribution.get_run_result(run_id=distribution_run_id)
        print("Distribution run result:\n{}".format(run_result))

        self.assertGreater(run_result.shape[0], 5)
        self.assertEqual(run_result.shape[1], 3)
        data_columns = run_result.columns.values
        self.assertIn("LoanPurpose", data_columns)
        self.assertIn("LoanDuration:avg", data_columns)
        self.assertIn("LoanAmount:avg", data_columns)

    def test_20_run_quality_monitor(self):
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

    def test_21_stats_on_quality_monitoring_table(self):
        self.subscription.quality_monitoring.print_table_schema()
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_table(limit=None)
        self.subscription.quality_monitoring.describe_table()

        quality_monitoring_table = self.subscription.quality_monitoring.get_table_content()
        assert_quality_monitoring_pandas_table_content(pandas_table_content=quality_monitoring_table)

        quality_metrics = self.subscription.quality_monitoring.get_table_content(format='python')
        assert_quality_monitoring_python_table_content(python_table_content=quality_metrics)

    def test_22_get_metrics(self):
        print("Old metrics:")
        print(self.ai_client.data_mart.get_deployment_metrics())
        print(self.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(self.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(self.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))

        ### BINARY CHECK

        metrics = {
            'threshold': None,
            'area_under_roc': None,
            'area_under_pr': None,
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
                print("Comparing metrics: {}".format(metric['id']))
                self.assertEqual(metric['value'], metrics[metric['id']], msg="metric {} has different value in ootb api".format(metric['id']))
                if 'lower_limit' in metric.keys():
                    self.assertEqual(metric['lower_limit'], metrics['threshold'], msg="lower_limit is not the same as threshold!")

        print(self.subscription.quality_monitoring.get_metrics(format="samples"))

    def test_23_get_performance_metrics(self):
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics())
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type='performance'))
        print(TestAIOpenScaleClient.subscription.performance_monitoring.get_metrics(deployment_uid=TestAIOpenScaleClient.subscription.get_deployment_uids()[0]))

        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics()['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type='performance')['deployment_metrics'][0]['metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.subscription.performance_monitoring.get_metrics(deployment_uid=TestAIOpenScaleClient.subscription.get_deployment_uids()[0])['metrics']) > 0)

    def test_24_disable_payload_logging_and_performance_monitoring(self):
        self.subscription.payload_logging.disable()
        self.subscription.performance_monitoring.disable()
        self.subscription.quality_monitoring.disable()

        subscription_details = self.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details)

    def test_25_unsubscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(TestAIOpenScaleClient.subscription.uid)

    def test_26_unbind(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.delete(TestAIOpenScaleClient.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
