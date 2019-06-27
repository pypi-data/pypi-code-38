# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import time

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import SPSSMachineLearningInstance, SPSSMachineLearningAsset
from ibm_ai_openscale.supporting_classes import ProblemType, InputDataType, PayloadRecord
from ibm_ai_openscale.utils.training_stats import TrainingStats
from preparation_and_cleaning import *


@unittest.skipIf("ICP" not in get_env(), "Please run this test only on ICP env")
class TestAIOpenScaleClient(unittest.TestCase):

    ai_client = None
    deployment_uid = None
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
    request = None
    response = None
    training_data_statistics = None
    # model_uid = 'german_credit_risk_tutorial'
    model_uid = 'german_credit_risk_tutorial'
    scoring_records = 12
    feedback_records = 18
    data_df = pd.read_csv(
        "./datasets/German_credit_risk/credit_risk_training.csv",
        dtype={'LoanDuration': int, 'LoanAmount': int, 'InstallmentPercent': int, 'CurrentResidenceDuration': int,
               'Age': int, 'ExistingCreditsCount': int, 'Dependents': int}
    )

    # SPSS C&DS
    credentials = get_spss_cnds_credentials()

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

        prepare_env(cls.ai_client)

    def test_01_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_02_data_mart_get_details(self):
        details = TestAIOpenScaleClient.ai_client.data_mart.get_details()
        print(details)
        self.assertTrue(len(json.dumps(details)) > 10)

    def test_03_bind_spss_cds_instance(self):
        TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("SPSS C&DS instance on ICP",
                                                                                  SPSSMachineLearningInstance(self.credentials))

    def test_04_get_binding_details(self):
        print('Binding details: :' + str(TestAIOpenScaleClient.ai_client.data_mart.bindings.get_details(TestAIOpenScaleClient.binding_uid)))
        TestAIOpenScaleClient.ai_client.data_mart.bindings.list()

    def test_05_get_assets(self):
        assets_uids = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_asset_uids()
        self.assertGreater(len(assets_uids), 1)
        print('Assets uids: ' + str(assets_uids))

        TestAIOpenScaleClient.ai_client.data_mart.bindings.list_assets()
        asset_details = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_asset_details()
        print('Assets details: ' + str(asset_details))

        TestAIOpenScaleClient.ai_client.data_mart.bindings.list_asset_deployments()

        for detail in asset_details:
            if self.model_uid == detail['name']:
                TestAIOpenScaleClient.source_uid = detail['source_uid']

        self.assertIsNotNone(TestAIOpenScaleClient.source_uid, msg="Asset with model uid: {} not found".format(self.model_uid))

    def test_06_subscribe_spss_asset(self):
        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            SPSSMachineLearningAsset(source_uid=TestAIOpenScaleClient.source_uid,
                                     binding_uid=TestAIOpenScaleClient.binding_uid,
                                     input_data_type=InputDataType.STRUCTURED,
                                     problem_type=ProblemType.BINARY_CLASSIFICATION,
                                     label_column="Risk",
                                     feature_columns=['CheckingStatus', 'LoanDuration', 'CreditHistory', 'LoanPurpose',
                                                      'LoanAmount',
                                                      'ExistingSavings', 'EmploymentDuration', 'InstallmentPercent',
                                                      'Sex', 'OthersOnLoan',
                                                      'CurrentResidenceDuration', 'OwnsProperty', 'Age',
                                                      'InstallmentPlans', 'Housing',
                                                      'ExistingCreditsCount', 'Job', 'Dependents', 'Telephone',
                                                      'ForeignWorker'],
                                     categorical_columns=['CheckingStatus', 'CreditHistory', 'LoanPurpose',
                                                          'ExistingSavings',
                                                          'EmploymentDuration', 'Sex', 'OthersOnLoan', 'OwnsProperty',
                                                          'InstallmentPlans',
                                                          'Housing', 'Job', 'Telephone', 'ForeignWorker'],
                                     prediction_column="$N-Risk",
                                     class_probability_columns=['$NC-Risk']
                                     ), deployment_uids='german_credit_risk_tutorial')

        TestAIOpenScaleClient.subscription_uid = subscription.uid
        print('Subscription details: ' + str(subscription.get_details()))

    def test_07_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.subscription_uid)
        print('Subscription details: ' + str(TestAIOpenScaleClient.subscription.get_details()))

    def test_08_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_09_score_and_log_payload(self):
        binding_details = self.ai_client.data_mart.bindings.get_details(self.binding_uid)
        binding_credentials = binding_details['entity']['credentials']
        self.assertEqual(self.credentials['username'], binding_credentials['username'])
        self.assertEqual(self.credentials['password'], binding_credentials['password'])
        self.assertEqual(self.credentials['url'], binding_credentials['url'])

        subscription_details = self.subscription.get_details()
        scoring_endpoint = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']
        input_table_id = subscription_details['entity']['asset_properties']['input_data_schema']['id']

        scoring_payload = {
            'id': self.model_uid,
            'requestInputTable': [
                {
                    'id': input_table_id,
                    'requestInputRow': [
                        {
                            'input': [
                                {
                                    'name': 'CheckingStatus',
                                    'value': '0_to_200'
                                },
                                {
                                    'name': 'LoanDuration',
                                    'value': '31'
                                },
                                {
                                    'name': 'CreditHistory',
                                    'value': 'credits_paid_to_date'
                                },
                                {
                                    'name': 'LoanPurpose',
                                    'value': 'other'
                                },
                                {
                                    'name': 'LoanAmount',
                                    'value': '1889'
                                },
                                {
                                    'name': 'ExistingSavings',
                                    'value': '100_to_500'
                                },
                                {
                                    'name': 'EmploymentDuration',
                                    'value': 'less_1'
                                },
                                {
                                    'name': 'InstallmentPercent',
                                    'value': '3'
                                },
                                {
                                    'name': 'Sex',
                                    'value': 'female'
                                },
                                {
                                    'name': 'OthersOnLoan',
                                    'value': 'none'
                                },
                                {
                                    'name': 'CurrentResidenceDuration',
                                    'value': '3'
                                },
                                {
                                    'name': 'OwnsProperty',
                                    'value': 'savings_insurance'
                                },
                                {
                                    'name': 'Age',
                                    'value': '32'
                                },
                                {
                                    'name': 'InstallmentPlans',
                                    'value': 'none'
                                },
                                {
                                    'name': 'Housing',
                                    'value': 'own'
                                },
                                {
                                    'name': 'ExistingCreditsCount',
                                    'value': '1'
                                },
                                {
                                    'name': 'Job',
                                    'value': 'skilled'
                                },
                                {
                                    'name': 'Dependents',
                                    'value': '1'
                                },
                                {
                                    'name': 'Telephone',
                                    'value': 'none'
                                },
                                {
                                    'name': 'ForeignWorker',
                                    'value': 'yes'
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        start_time = time.time()
        resp_score = requests.post(url=scoring_endpoint, json=scoring_payload, auth=HTTPBasicAuth(username=binding_credentials['username'], password=binding_credentials['password']))
        response_time = time.time() - start_time
        result = resp_score.json()

        print('Scoring result:', result)

        TestAIOpenScaleClient.request = scoring_payload
        TestAIOpenScaleClient.response = result

        records_list = []

        for i in range(0, self.scoring_records):
            records_list.append(PayloadRecord(request=TestAIOpenScaleClient.request, response=TestAIOpenScaleClient.response, response_time=int(response_time)))

        self.subscription.payload_logging.store(records=records_list)

        wait_for_payload_table(subscription=self.subscription, payload_records=self.scoring_records)

    def test_10_stats_on_payload_logging_table(self):
        TestAIOpenScaleClient.subscription.payload_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.payload_logging.show_table()
        TestAIOpenScaleClient.subscription.payload_logging.describe_table()

        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content,
                                                    scoring_records=self.scoring_records)

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        assert_payload_logging_python_table_content(python_table_content=python_table_content,
                                                    fields=['$N-Risk', '$NC-Risk', '$NP-No Risk', '$NP-Risk'])

    def test_11_setup_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.enable(threshold=0.8, min_records=5)

    def test_12_get_quality_monitoring_details(self):
        print(str(TestAIOpenScaleClient.subscription.quality_monitoring.get_details()))
        TestAIOpenScaleClient.subscription.quality_monitoring.get_details()

    def test_13_send_feedback_data(self):
        from ibm_ai_openscale.supporting_classes.enums import FeedbackFormat

        dict_record = {
            'LoanAmount': '1889',
            'ExistingSavings': '100_to_500',
            'OwnsProperty': 'savings_insurance',
            'Risk': 'Risk',
            'OthersOnLoan': 'none',
            'Telephone': 'none',
            'CurrentResidenceDuration': '3',
            'Age': '32',
            'InstallmentPlans': 'none',
            'EmploymentDuration': 'less_1',
            'ExistingCreditsCount': '1',
            'Sex': 'female',
            'LoanPurpose': 'other',
            'CheckingStatus': '0_to_200',
            'CreditHistory': 'credits_paid_to_date',
            'Housing': 'own',
            'Job': 'skilled',
            'LoanDuration': '31',
            'InstallmentPercent': '3',
            'Dependents': '1',
            'ForeignWorker': 'yes'
        }

        feedback_data = []
        for i in range(0, 10):
            feedback_data.append(dict_record)

        TestAIOpenScaleClient.subscription.feedback_logging.store(feedback_data=feedback_data, feedback_format=FeedbackFormat.DICT)

        wait_for_feedback_table(subscription=self.subscription, feedback_records=self.feedback_records)

    def test_14_stats_on_feedback_logging_table(self):
        TestAIOpenScaleClient.subscription.feedback_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.feedback_logging.show_table()
        TestAIOpenScaleClient.subscription.feedback_logging.describe_table()
        TestAIOpenScaleClient.subscription.feedback_logging.get_table_content()
        feedback_logging = TestAIOpenScaleClient.subscription.feedback_logging.get_table_content(format='python')
        self.assertTrue(len(feedback_logging['values']) > 0)

    def test_15_run_quality_monitor(self):
        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run()
        assert_quality_entire_run(subscription=self.subscription, run_details=run_details)

    def test_16_stats_on_quality_monitoring_table(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table(limit=None)
        TestAIOpenScaleClient.subscription.quality_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content()
        quality_metrics = TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue(len(quality_metrics['values']) > 0)

    def test_18_get_quality_metrics(self):
        deployment_uid = TestAIOpenScaleClient.subscription.get_deployment_uids()[0]

        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics())
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type='quality'))
        print(TestAIOpenScaleClient.subscription.quality_monitoring.get_metrics(deployment_uid=deployment_uid))

        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics()['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type='quality')['deployment_metrics'][0]['metrics']) > 0)

    def test_19_stats_on_performance_metrics(self):
        TestAIOpenScaleClient.subscription.performance_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.performance_monitoring.show_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_20_get_performance_metrics(self):
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
            deployment_uid=TestAIOpenScaleClient.subscription.get_deployment_uids()[0]))

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
            deployment_uid=TestAIOpenScaleClient.subscription.get_deployment_uids()[0])['metrics']) > 0)

    def test_21_setup_explainability(self):
        TestAIOpenScaleClient.training_data_statistics = TrainingStats(
            TestAIOpenScaleClient.data_df,
            {
                "problem_type": ProblemType.BINARY_CLASSIFICATION,
                "label_column": 'Risk',
                "feature_columns": ['CheckingStatus', 'LoanDuration', 'CreditHistory', 'LoanPurpose', 'LoanAmount',
                                    'ExistingSavings', 'EmploymentDuration', 'InstallmentPercent', 'Sex',
                                    'OthersOnLoan', 'CurrentResidenceDuration', 'OwnsProperty', 'Age',
                                    'InstallmentPlans', 'Housing', 'ExistingCreditsCount', 'Job', 'Dependents',
                                    'Telephone', 'ForeignWorker'],
                "categorical_columns": ['CheckingStatus', 'CreditHistory', 'LoanPurpose', 'ExistingSavings',
                                        'EmploymentDuration', 'Sex', 'OthersOnLoan', 'OwnsProperty',
                                        'InstallmentPlans', 'Housing', 'Job', 'Telephone', 'ForeignWorker'],
                "fairness_inputs": {
                    "fairness_attributes": [
                        {
                            "majority": [[26,75]],
                            "minority": [[18,25]],
                            "type": "int",
                            "feature": "Age",
                            "threshold": 0.95
                        },
                        {
                            "majority": ["male"],
                            "minority": ["female"],
                            "type": "string",
                            "feature": "Sex",
                            "threshold": 0.95
                        }
                    ],
                    "min_records": 4,
                    "favourable_class": ['No Risk'],
                    "unfavourable_class": ['Risk']

                }
            }
        ).get_training_statistics()

        print(TestAIOpenScaleClient.training_data_statistics)

        TestAIOpenScaleClient.subscription.explainability.enable(
            training_data_statistics=TestAIOpenScaleClient.training_data_statistics
        )

    def test_22_get_details(self):
        details = TestAIOpenScaleClient.subscription.explainability.get_details()
        assert_explainability_configuration(explainability_details=details)

    def test_23_get_transaction_id(self):
        pandas_pd = self.subscription.payload_logging.get_table_content()
        no_payloads = len(pandas_pd['scoring_id'].values)

        # select random record from payload table
        import random
        random_record = random.randint(0, no_payloads-1)
        TestAIOpenScaleClient.transaction_id = pandas_pd['scoring_id'].values[random_record]

        print("Selected trainsaction id: {}".format(self.transaction_id))

    def test_24_run_explainability(self):
        explainability_run = TestAIOpenScaleClient.subscription.explainability.run(
            transaction_id=self.transaction_id,
            background_mode=False
        )
        assert_explainability_run(explainability_run_details=explainability_run)

    def test_24b_list_explanations(self):
        TestAIOpenScaleClient.subscription.explainability.list_explanations()

    def test_25_stats_on_explainability_table(self):
        TestAIOpenScaleClient.subscription.explainability.print_table_schema()
        TestAIOpenScaleClient.subscription.explainability.show_table()
        TestAIOpenScaleClient.subscription.explainability.describe_table()

        pandas_df = TestAIOpenScaleClient.subscription.explainability.get_table_content()
        assert_explainability_pandas_table_content(pandas_table_content=pandas_df)

        python_table_content = TestAIOpenScaleClient.subscription.explainability.get_table_content(format='python')
        assert_explainability_python_table_content(python_table_content=python_table_content)

    def test_26_setup_fairness_monitoring(self):
        from ibm_ai_openscale.supporting_classes import Feature

        TestAIOpenScaleClient.subscription.fairness_monitoring.enable(
            features=[
                Feature("Sex", majority=['male'], minority=['female'], threshold=0.95),
                Feature("Age", majority=[[26, 75]], minority=[[18, 25]], threshold=0.95)
            ],
            deployment_uid=self.model_uid,
            favourable_classes=['No Risk'],
            unfavourable_classes=['Risk'],
            min_records=4,
            training_data_statistics=TestAIOpenScaleClient.training_data_statistics
        )

    def test_27_get_fairness_monitoring_details(self):
        details = TestAIOpenScaleClient.subscription.fairness_monitoring.get_details()
        assert_fairness_configuration(fairness_monitoring_details=details)

    def test_28_run_fairness(self):
        fairness_run = TestAIOpenScaleClient.subscription.fairness_monitoring.run(
            background_mode=False)
        assert_fairness_run(fairness_run_details=fairness_run)

    def test_29_stats_on_fairness_monitoring_table(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.fairness_monitoring.show_table()
        TestAIOpenScaleClient.subscription.fairness_monitoring.describe_table()

        pandas_df = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content()
        assert_fairness_monitoring_pandas_table_content(pandas_table_content=pandas_df)

        python_table_content = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content(format='python')
        assert_fairness_monitoring_python_table_content(python_table_content=python_table_content)

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
