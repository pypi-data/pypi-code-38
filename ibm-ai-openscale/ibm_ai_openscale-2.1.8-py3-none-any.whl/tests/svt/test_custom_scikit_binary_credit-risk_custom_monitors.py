# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import requests
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from assertions import *
import pandas as pd
import random


class TestAIOpenScaleClient(unittest.TestCase):
    log_loss_random = None
    brier_score_loss = None
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
    monitor_uid = None
    source_uid = None
    transaction_id = None
    data_df = pd.read_csv(
        "./datasets/German_credit_risk/credit_risk_training.csv",
        dtype={'LoanDuration': int, 'LoanAmount': int, 'InstallmentPercent': int, 'CurrentResidenceDuration': int,
               'Age': int, 'ExistingCreditsCount': int, 'Dependents': int})

    test_uid = str(uuid.uuid4())

    # Custom deployment configuration
    credentials = {
        "url": "http://169.63.194.147:31520",
        "username": "xxx",
        "password": "yyy",
        "request_headers": {"content-type": "application/json"}
    }

    image_path = os.path.join(os.getcwd(), 'datasets', 'images', 'labrador.jpg')

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
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer xxx'}
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
        print('Available deployments: {}'.format(self.ai_client.data_mart.bindings.get_asset_deployment_details()))
        self.ai_client.data_mart.bindings.list_assets()
        self.ai_client.data_mart.bindings.get_asset_details()

    def test_05_subscribe_custom(self):
        subscription = self.ai_client.data_mart.subscriptions.add(
            CustomMachineLearningAsset(
                source_uid='credit',
                label_column='Risk',
                prediction_column='prediction',
                probability_column='probability',
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
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)

    def test_07_list_deployments(self):
        print("Listing deployments:\n")
        self.subscription.list_deployments()

    def test_08_register_custom_monitor_without_defaults(self):
        from ibm_ai_openscale.supporting_classes import Metric, Tag

        metrics = [Metric(name='log_loss'), Metric(name='brier_score_loss')]
        tags = [Tag(name='region', description='customer geographical region')]

        my_monitor = self.ai_client.data_mart.monitors.add(name='model performance', metrics=metrics, tags=tags)
        print('monitor definition details', my_monitor)

        print('all details', self.ai_client.data_mart.monitors.get_details())

        TestAIOpenScaleClient.monitor_uid = self.ai_client.data_mart.monitors.get_uids(name='model performance')[0]
        print('monitor_uid', TestAIOpenScaleClient.monitor_uid)

        self.assertIsNotNone(my_monitor)
        self.assertIsNotNone(TestAIOpenScaleClient.monitor_uid)

    def test_09_list_custom_monitors(self):
        self.ai_client.data_mart.monitors.list()

    def test_10_get_custom_monitor_details(self):
        my_monitor = self.ai_client.data_mart.monitors.get_details(TestAIOpenScaleClient.monitor_uid)
        print("Monitor definition details: {}".format(my_monitor))

        self.assertTrue('model performance' in str(my_monitor))

    def test_11_enable_monitoring(self):
        from ibm_ai_openscale.supporting_classes import Threshold

        thresholds = [Threshold(metric_uid='log_loss', lower_limit=0.2)]
        TestAIOpenScaleClient.subscription.monitoring.enable(TestAIOpenScaleClient.monitor_uid, thresholds=thresholds)

        assert_custom_monitor_enablement(subscription_details=self.subscription.get_details(), monitor_uid=self.monitor_uid)

    def test_12_get_monitoring_details(self):
        details = TestAIOpenScaleClient.subscription.monitoring.get_details(monitor_uid=TestAIOpenScaleClient.monitor_uid)
        print('Custom monitoring details: {}'.format(details))

        self.assertIsNotNone(details)

    def test_13_store_custom_metrics(self):
        TestAIOpenScaleClient.log_loss_random = float("{0:.2f}".format(random.random()))
        TestAIOpenScaleClient.brier_score_loss = float("{0:.2f}".format(random.random()))
        metrics = {"log_loss": self.log_loss_random, "brier_score_loss": self.brier_score_loss, "region": "us-south"}
        self.subscription.monitoring.store_metrics(monitor_uid=TestAIOpenScaleClient.monitor_uid, metrics=metrics)

        for i in range(0, 10):
            metrics = {"log_loss": float("{0:.2f}".format(random.random())), "brier_score_loss": float("{0:.2f}".format(random.random())), "region": "uk-brexit"}
            self.subscription.monitoring.store_metrics(monitor_uid=TestAIOpenScaleClient.monitor_uid, metrics=metrics)

    def test_14_get_custom_metrics(self):
        self.subscription.monitoring.show_table(monitor_uid=TestAIOpenScaleClient.monitor_uid)
        self.subscription.monitoring.print_table_schema()
        self.subscription.monitoring.describe_table(monitor_uid=TestAIOpenScaleClient.monitor_uid)

        metrics = self.subscription.monitoring.get_metrics(deployment_uid=self.deployment_uid, monitor_uid=self.monitor_uid, format='samples')
        print("Metrics:\n{}".format(metrics))

        metric_json = {
            'lower_limit': 0.2,
            'id': 'log_loss',
            'value': self.log_loss_random,
        }
        assert_metric(metrics_content=metrics, metric_json=metric_json, binding_id=self.binding_uid, monitor_definition_id=self.monitor_uid)

        metric_json = {
            'id': 'brier_score_loss',
            'value': self.brier_score_loss,
        }
        assert_metric(metrics_content=metrics, metric_json=metric_json, binding_id=self.binding_uid, monitor_definition_id=self.monitor_uid)

        metrics = self.subscription.monitoring.get_metrics(deployment_uid=self.deployment_uid, monitor_uid=self.monitor_uid, format='time_series')

        print("Metrics timeseries:\n{}".format(metrics))

        pd_df = TestAIOpenScaleClient.subscription.monitoring.get_table_content(monitor_uid=TestAIOpenScaleClient.monitor_uid)
        assert_metrics_pandas_table_content(pandas_table_content=pd_df, metrics_records=22)

        python_df = TestAIOpenScaleClient.subscription.monitoring.get_table_content(monitor_uid=TestAIOpenScaleClient.monitor_uid, format="python")
        assert_metrics_python_table_content(python_table_content=python_df, metrics=["log_loss", "brier_score_loss"], metrics_values=[self.log_loss_random, self.brier_score_loss])

    def test_15_disable_monitoring(self):
        TestAIOpenScaleClient.subscription.monitoring.disable(TestAIOpenScaleClient.monitor_uid)

    def test_16_list_custom_monitors(self):
        self.ai_client.data_mart.monitors.list()

    def test_17_get_custom_monitors(self):
        print(self.ai_client.data_mart.monitors.get_details())

        assert_custom_monitor_enablement(subscription_details=self.subscription.get_details(), monitor_uid=self.monitor_uid, enabled=False)

    def test_18_store_custom_metrics(self):
        TestAIOpenScaleClient.log_loss_random = float("{0:.2f}".format(random.random()))
        TestAIOpenScaleClient.brier_score_loss = float("{0:.2f}".format(random.random()))
        metrics = {"log_loss": self.log_loss_random, "brier_score_loss": self.brier_score_loss, "region": "us-south"}
        self.subscription.monitoring.store_metrics(monitor_uid=TestAIOpenScaleClient.monitor_uid, metrics=metrics)

        for i in range(0, 10):
            metrics = {"log_loss": float("{0:.2f}".format(random.random())), "brier_score_loss": float("{0:.2f}".format(random.random())), "region": "uk-brexit"}
            self.subscription.monitoring.store_metrics(monitor_uid=TestAIOpenScaleClient.monitor_uid, metrics=metrics)

    def test_19_get_custom_monitor_details(self):
        my_monitor = self.ai_client.data_mart.monitors.get_details(TestAIOpenScaleClient.monitor_uid)
        print('monitor definition details', my_monitor)

        self.assertTrue('model performance' in str(my_monitor))

    def test_20_enable_monitoring(self):
        from ibm_ai_openscale.supporting_classes import Threshold

        thresholds = [Threshold(metric_uid='log_loss', lower_limit=0.2)]
        TestAIOpenScaleClient.subscription.monitoring.enable(TestAIOpenScaleClient.monitor_uid, thresholds=thresholds)

        assert_custom_monitor_enablement(subscription_details=self.subscription.get_details(), monitor_uid=self.monitor_uid)

    def test_21_get_monitoring_details(self):
        details = TestAIOpenScaleClient.subscription.monitoring.get_details(monitor_uid=TestAIOpenScaleClient.monitor_uid)
        print('custom monitoring', details)

        self.assertIsNotNone(details)

    def test_22_store_custom_metrics(self):
        metrics = {"log_loss": 0.78, "brier_score_loss": 0.67, "region": "us-south"}
        TestAIOpenScaleClient.subscription.monitoring.store_metrics(monitor_uid=TestAIOpenScaleClient.monitor_uid, metrics=metrics)

        for i in range(0,10):
            TestAIOpenScaleClient.subscription.monitoring.store_metrics(monitor_uid=TestAIOpenScaleClient.monitor_uid, metrics=metrics)

    def test_23_get_custom_metrics(self):
        metrics = TestAIOpenScaleClient.subscription.monitoring.get_metrics(
            deployment_uid=TestAIOpenScaleClient.deployment_uid, monitor_uid=TestAIOpenScaleClient.monitor_uid)
        print('metrics', metrics)
        self.assertTrue('0.78' in str(metrics))

        TestAIOpenScaleClient.subscription.monitoring.show_table(monitor_uid=TestAIOpenScaleClient.monitor_uid)
        pd_df = TestAIOpenScaleClient.subscription.monitoring.get_table_content(monitor_uid=TestAIOpenScaleClient.monitor_uid)
        print('pd_df.shape', pd_df.shape)
        self.assertTrue('(' in str(pd_df.shape))

        TestAIOpenScaleClient.subscription.monitoring.print_table_schema()

    def test_24_register_custom_monitor(self):
        from ibm_ai_openscale.supporting_classes import Metric, Tag

        metrics = [Metric(name='echo_log_loss', lower_limit_default=0.4, upper_limit_default=0.8), Metric(name='echo_brier_score_loss', lower_limit_default=0.75, upper_limit_default=0.92)]
        tags = [Tag(name='framework', description='framework used for implementation'), Tag(name='language', description='programming language used for implementation', required=False)]

        my_monitor = self.ai_client.data_mart.monitors.add(name='echo model validation', metrics=metrics, tags=tags)
        print('monitor definition details', my_monitor)

        print('all details', self.ai_client.data_mart.monitors.get_details())

        TestAIOpenScaleClient.monitor_uid = self.ai_client.data_mart.monitors.get_uids(name='echo model validation')[0]
        print('monitor_uid', TestAIOpenScaleClient.monitor_uid)

        self.assertIsNotNone(my_monitor)
        self.assertIsNotNone(TestAIOpenScaleClient.monitor_uid)

    def test_25_enable_monitoring(self):
        from ibm_ai_openscale.supporting_classes import Threshold

        thresholds = [Threshold(metric_uid='echo_log_loss', lower_limit=0.3), Threshold(metric_uid='echo_brier_score_loss', upper_limit=0.88)]
        TestAIOpenScaleClient.subscription.monitoring.enable(TestAIOpenScaleClient.monitor_uid, thresholds=thresholds)

        assert_custom_monitor_enablement(subscription_details=self.subscription.get_details(), monitor_uid=self.monitor_uid)

    def test_26_list_custom_monitors(self):
        self.ai_client.data_mart.monitors.list()

    def test_27_get_monitoring_details(self):
        details = TestAIOpenScaleClient.subscription.monitoring.get_details(monitor_uid=TestAIOpenScaleClient.monitor_uid)
        print('custom monitoring', details)

        self.assertIsNotNone(details)

    def test_28_store_custom_metrics(self):
        metrics = {"echo_log_loss": 0.03, "echo_brier_score_loss": 0.31, "framework": "tensorflow"}
        TestAIOpenScaleClient.subscription.monitoring.store_metrics(monitor_uid=TestAIOpenScaleClient.monitor_uid, metrics=metrics)

        for i in range(0, 10):
            metrics = {"echo_log_loss": float("{0:.2f}".format(random.random())), "echo_brier_score_loss": float("{0:.2f}".format(random.random())), "framework": "keras", "language": "R"}
            TestAIOpenScaleClient.subscription.monitoring.store_metrics(monitor_uid=TestAIOpenScaleClient.monitor_uid, metrics=metrics)

    def test_29_get_custom_metrics(self):
        self.subscription.monitoring.show_table(monitor_uid=TestAIOpenScaleClient.monitor_uid)
        self.subscription.monitoring.print_table_schema()
        self.subscription.monitoring.describe_table(monitor_uid=TestAIOpenScaleClient.monitor_uid)

        metrics = self.subscription.monitoring.get_metrics(deployment_uid=self.deployment_uid, monitor_uid=self.monitor_uid, format='samples')
        print("Metrics:\n{}".format(metrics))

        metric_json = {
            'lower_limit': 0.3,
            'id': 'echo_log_loss',
            'value': 0.03,
        }
        assert_metric(metrics_content=metrics, metric_json=metric_json, binding_id=self.binding_uid, monitor_definition_id=self.monitor_uid)

        metric_json = {
            'id': 'echo_brier_score_loss',
            'value': 0.31,
            'upper_limit': 0.88,
        }
        assert_metric(metrics_content=metrics, metric_json=metric_json, binding_id=self.binding_uid, monitor_definition_id=self.monitor_uid)

        metrics = self.subscription.monitoring.get_metrics(deployment_uid=self.deployment_uid, monitor_uid=self.monitor_uid, format='time_series')

        print("Metrics timeseries:\n{}".format(metrics))

        pd_df = TestAIOpenScaleClient.subscription.monitoring.get_table_content(monitor_uid=TestAIOpenScaleClient.monitor_uid)
        assert_metrics_pandas_table_content(pandas_table_content=pd_df, metrics_records=22)

        # python_df = TestAIOpenScaleClient.subscription.monitoring.get_table_content(monitor_uid=TestAIOpenScaleClient.monitor_uid, format="python")
        # assert_metrics_python_table_content(python_table_content=python_df, metrics=["echo_log_loss", "echo_brier_score_loss"], metrics_values=[self.log_loss_random, self.brier_score_loss])

    def test_30_check_issues(self):
        self.ai_client.data_mart.show_issues()

    def test_34_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_35_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
