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
from ibm_ai_openscale.supporting_classes.enums import *
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
    transaction_id = None
    feedback_records = None
    start_date = datetime.utcnow().isoformat() + 'Z'

    data_df = pd.read_csv(
        "./datasets/German_credit_risk/credit_risk_training.csv",
        dtype={'LoanDuration': int, 'LoanAmount': int, 'InstallmentPercent': int, 'CurrentResidenceDuration': int,
               'Age': int, 'ExistingCreditsCount': int, 'Dependents': int})

    test_uid = str(uuid.uuid4())

    # Custom deployment configuration
    credentials = {
        "url": "http://custom-engine-for-openscale.azurewebsites.net",
        "request_headers": {"content-type": "application/json"}
    }

    def score(self, subscription_details):
        fields = ["CheckingStatus", "LoanDuration", "CreditHistory", "LoanPurpose", "LoanAmount", "ExistingSavings",
                  "EmploymentDuration", "InstallmentPercent", "Sex", "OthersOnLoan", "CurrentResidenceDuration",
                  "OwnsProperty", "Age", "InstallmentPlans", "Housing", "ExistingCreditsCount", "Job", "Dependents",
                  "Telephone", "ForeignWorker"]
        values = [
            ["no_checking", 13, "credits_paid_to_date", "car_new", 1343, "100_to_500", "1_to_4", 2, "female", "none", 3,
             "savings_insurance", 25, "none", "own", 2, "skilled", 1, "none", "yes"],
            ["no_checking", 24, "prior_payments_delayed", "furniture", 4567, "500_to_1000", "1_to_4", 4, "male", "none",
             4, "savings_insurance", 60, "none", "free", 2, "management_self-employed", 1, "none", "yes"],
            ["0_to_200", 26, "all_credits_paid_back", "car_new", 863, "less_100", "less_1", 2, "female", "co-applicant",
             2, "real_estate", 38, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["0_to_200", 14, "no_credits", "car_new", 2368, "less_100", "1_to_4", 3, "female", "none", 3, "real_estate",
             29, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["0_to_200", 4, "no_credits", "car_new", 250, "less_100", "unemployed", 2, "female", "none", 3,
             "real_estate", 23, "none", "rent", 1, "management_self-employed", 1, "none", "yes"],
            ["no_checking", 17, "credits_paid_to_date", "car_new", 832, "100_to_500", "1_to_4", 2, "male", "none", 2,
             "real_estate", 42, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["no_checking", 50, "outstanding_credit", "appliances", 5696, "unknown", "greater_7", 4, "female",
             "co-applicant", 4, "unknown", 54, "none", "free", 2, "skilled", 1, "yes", "yes"],
            ["0_to_200", 13, "prior_payments_delayed", "retraining", 1375, "100_to_500", "4_to_7", 3, "male", "none", 3,
             "real_estate", 70, "none", "own", 2, "management_self-employed", 1, "none", "yes"]
        ]

        payload = {"fields": fields, "values": values}
        header = {'Content-Type': 'application/json'}
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

        response = requests.post(scoring_url, json=payload, headers=header)

        return payload, response.json(), 25

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
        self.ai_client.data_mart.bindings.get_asset_details()

    def test_05_subscribe_custom(self):
        subscription = self.ai_client.data_mart.subscriptions.add(
            CustomMachineLearningAsset(
                source_uid='credit',
                label_column='Risk',
                prediction_column='Scored Labels',
                probability_column='Scored Probabilities',
                feature_columns=['CheckingStatus', 'LoanDuration', 'CreditHistory', 'LoanPurpose', 'LoanAmount',
                                 'ExistingSavings', 'EmploymentDuration', 'InstallmentPercent', 'Sex', 'OthersOnLoan',
                                 'CurrentResidenceDuration', 'OwnsProperty', 'Age', 'InstallmentPlans', 'Housing',
                                 'ExistingCreditsCount', 'Job', 'Dependents', 'Telephone', 'ForeignWorker'],
                categorical_columns=['CheckingStatus', 'CreditHistory', 'LoanPurpose', 'ExistingSavings',
                                     'EmploymentDuration', 'Sex', 'OthersOnLoan', 'OwnsProperty', 'InstallmentPlans',
                                     'Housing', 'Job', 'Telephone', 'ForeignWorker'],
                binding_uid=self.binding_uid))

        TestAIOpenScaleClient.subscription_uid = subscription.uid
        print('Subscription details: ', subscription.get_details())
        print("Subscription id: {}".format(self.subscription_uid))
        self.assertIsNotNone(self.subscription_uid)

    def test_06_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.subscription_uid)
        self.assertIsNotNone(self.subscription)

    def test_07_list_deployments(self):
        print("Listing deployments:\n")
        self.subscription.list_deployments()

    def test_08_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        for configuration in subscription_details['entity']['configurations']:
            if configuration['type'] == 'payload_logging' or configuration['type'] == 'performance_monitoring':
                self.assertEqual(configuration['enabled'], True)
            else:
                self.assertEqual(configuration['enabled'], False)

    def test_09_score_model_and_log_payload(self):
        request, response, response_time = self.score(self.subscription.get_details())

        print('response: ' + str(response))

        records_list = []

        for i in range(0, 20):
            records_list.append(PayloadRecord(request=request, response=response, response_time=response_time))

        self.subscription.payload_logging.store(records=records_list)
        wait_for_payload_propagation(is_wml_engine=False)

    def test_10_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        self.subscription.payload_logging.show_table()
        self.subscription.payload_logging.describe_table()

        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content,
                                                    scoring_records=160)

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        assert_payload_logging_python_table_content(python_table_content=python_table_content,
                                                    fields=['Scored Labels', 'Scored Probabilities', 'Job', 'InstallmentPlans'])

        print('subscription details', TestAIOpenScaleClient.subscription.get_details())

    def test_11_payload_logging_data_distribution(self):
        end_date = datetime.utcnow().isoformat() + "Z"
        sex_distribution_run = TestAIOpenScaleClient.subscription.payload_logging.data_distribution.run(
            start_date=TestAIOpenScaleClient.start_date,
            end_date=end_date,
            group=['Age', 'Sex'],
            agg=['LoanAmount:stddev', 'LoanDuration:max', 'LoanAmount:avg'])

        run_id = sex_distribution_run['id']
        sex_distribution = self.subscription.payload_logging.data_distribution.get_run_result(run_id=run_id)

        print('Payload data distribution')
        print(sex_distribution)

        self.assertEqual(sex_distribution.shape[0], 8)
        self.assertEqual(sex_distribution.shape[1], 5)
        data_columns = sex_distribution.columns.values
        self.assertIn("Age", data_columns)
        self.assertIn("Sex", data_columns)
        self.assertIn("LoanAmount:stddev", data_columns)
        self.assertIn("LoanDuration:max", data_columns)
        self.assertIn("LoanAmount:avg", data_columns)

    def test_12_stats_on_performance_monitoring_table(self):
        self.subscription.performance_monitoring.print_table_schema()
        self.subscription.performance_monitoring.show_table()
        self.subscription.performance_monitoring.describe_table()
        self.subscription.performance_monitoring.get_table_content()
        performance_metrics = self.subscription.performance_monitoring.get_table_content(format='python')
        self.assertTrue(len(performance_metrics['values']) > 0)

    def test_13_enable_quality_monitoring(self):
        self.subscription.quality_monitoring.enable(threshold=0.7, min_records=5)
        details = self.subscription.quality_monitoring.get_details()
        self.assertTrue('True' in str(details))

    def test_14_feedback_logging(self):
        TestAIOpenScaleClient.feedback_records = 50

        training_data = pd.read_csv('datasets/German_credit_risk/credit_risk_training_500.csv')

        self.subscription.feedback_logging.store(
            feedback_data=training_data.sample(n=self.feedback_records).to_csv(index=False),
            feedback_format=FeedbackFormat.CSV,
            data_header=True,
            data_delimiter=',')

        print("Waiting 30 seconds for propagation.")
        time.sleep(10)

    def test_15_stats_on_feedback_logging(self):
        self.subscription.feedback_logging.show_table()
        self.subscription.feedback_logging.print_table_schema()
        self.subscription.feedback_logging.describe_table()
        self.subscription.feedback_logging.show_table()
        assert_feedback_logging_unstructured_data(subscription=self.subscription, feedback_records=self.feedback_records)

    def test_16_feedback_logging_data_distribution(self):
        end_date = datetime.utcnow().isoformat() + "Z"
        sex_distribution_run = TestAIOpenScaleClient.subscription.feedback_logging.data_distribution.run(
            start_date=TestAIOpenScaleClient.start_date,
            end_date=end_date,
            group=['Risk', 'Sex'],
            agg=['count', 'LoanAmount:avg'])

        run_id = sex_distribution_run['id']
        sex_distribution = self.subscription.feedback_logging.data_distribution.get_run_result(run_id=run_id)

        print("Feedback data distribution:")
        print(sex_distribution)

        self.assertEqual(sex_distribution.shape[0], 4)
        self.assertEqual(sex_distribution.shape[1], 4)

    def test_17_run_quality_monitoring(self):
        run_details = self.subscription.quality_monitoring.run()
        assert_quality_run(run_details=run_details)

        status = run_details['status']
        id = run_details['id']
        start_time = time.time()
        elapsed_time = 0

        while status != 'completed' and elapsed_time < 60:
            time.sleep(10)
            run_details = self.subscription.quality_monitoring.get_run_details(run_uid=id)
            print("Run details: {}".format(run_details))
            status = run_details['status']
            print("Status: {}".format(status))
            elapsed_time = time.time() - start_time
            self.assertNotIn('failed', status)

        self.assertIn('completed', status)

    def test_18_stats_on_quality_monitoring_table(self):
        self.subscription.quality_monitoring.print_table_schema()
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_table(limit=None)
        self.subscription.quality_monitoring.describe_table()
        self.subscription.quality_monitoring.get_table_content()
        quality_metrics = self.subscription.quality_monitoring.get_table_content(format='python')
        self.assertGreater(len(quality_metrics['values']), 0)

    def test_19_get_metrics(self):
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
                self.assertEqual(metric['value'], metrics[metric['id']],
                                 msg="metric {} has different value in ootb api".format(metric['id']))
                if 'lower_limit' in metric.keys():
                    self.assertEqual(metric['lower_limit'], metrics['threshold'],
                                     msg="lower_limit is not the same as threshold!")

        print(self.subscription.quality_monitoring.get_metrics(format="samples"))

    def test_20_setup_explainability(self):
        self.assertIsNotNone(TestAIOpenScaleClient.data_df)
        TestAIOpenScaleClient.subscription.explainability.enable(training_data=TestAIOpenScaleClient.data_df)

    def test_21_get_details(self):
        details = TestAIOpenScaleClient.subscription.explainability.get_details()
        assert_explainability_configuration(explainability_details=details)

    def test_22_get_transaction_id(self):
        pandas_pd = self.subscription.payload_logging.get_table_content()
        no_payloads = len(pandas_pd['scoring_id'].values)

        # select random record from payload table
        import random
        random_record = random.randint(0, no_payloads-1)
        TestAIOpenScaleClient.transaction_id = pandas_pd['scoring_id'].values[random_record]

        print("Selected trainsaction id: {}".format(self.transaction_id))

    def test_23_run_explainability(self):
        explainability_run = TestAIOpenScaleClient.subscription.explainability.run(
            transaction_id=self.transaction_id,
            background_mode=False
        )
        assert_explainability_run(explainability_run_details=explainability_run)

    def test_23b_list_explanations(self):
        TestAIOpenScaleClient.subscription.explainability.list_explanations()

    def test_24_stats_on_explainability_table(self):
        TestAIOpenScaleClient.subscription.explainability.print_table_schema()
        TestAIOpenScaleClient.subscription.explainability.show_table()
        TestAIOpenScaleClient.subscription.explainability.describe_table()

        pandas_df = TestAIOpenScaleClient.subscription.explainability.get_table_content()
        assert_explainability_pandas_table_content(pandas_table_content=pandas_df)

        python_table_content = TestAIOpenScaleClient.subscription.explainability.get_table_content(format='python')
        assert_explainability_python_table_content(python_table_content=python_table_content)

    def test_25_setup_fairness_monitoring(self):
        from ibm_ai_openscale.supporting_classes import Feature

        self.assertIsNotNone(TestAIOpenScaleClient.data_df)

        TestAIOpenScaleClient.subscription.fairness_monitoring.enable(
            features=[
                Feature("Sex", majority=['male'], minority=['female'], threshold=0.95),
                Feature("Age", majority=[[26, 75]], minority=[[18, 25]], threshold=0.95)
            ],
            favourable_classes=['No Risk'],
            unfavourable_classes=['Risk'],
            min_records=4,
            training_data=TestAIOpenScaleClient.data_df
        )

    def test_26_get_fairness_monitoring_details(self):
        details = TestAIOpenScaleClient.subscription.fairness_monitoring.get_details()
        assert_fairness_configuration(fairness_monitoring_details=details)

    def test_27_run_fairness(self):
        fairness_run = TestAIOpenScaleClient.subscription.fairness_monitoring.run(background_mode=False)
        assert_fairness_run(fairness_run_details=fairness_run)

    def test_28_stats_on_fairness_monitoring_table(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.fairness_monitoring.show_table()
        TestAIOpenScaleClient.subscription.fairness_monitoring.describe_table()

        pandas_df = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content()
        assert_fairness_monitoring_pandas_table_content(pandas_table_content=pandas_df)

        python_table_content = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content(format='python')
        assert_fairness_monitoring_python_table_content(python_table_content=python_table_content)

    def test_29_get_metrics(self):
        quality_metrics_asset_uid = self.ai_client.data_mart.get_deployment_metrics(asset_uid=self.subscription.source_uid, metric_type='quality')

        print(quality_metrics_asset_uid)

        self.assertGreater(len(quality_metrics_asset_uid['deployment_metrics'][0]['metrics']), 0)

    def test_30_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_31_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
