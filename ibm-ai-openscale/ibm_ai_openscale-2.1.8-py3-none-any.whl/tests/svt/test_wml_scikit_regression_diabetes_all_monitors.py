# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import pandas as pd

from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType
from ibm_ai_openscale.supporting_classes.feature import Feature
from preparation_and_cleaning import *
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score


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
    scoring_records = 20
    feedback_records = 10
    label_column = None
    feature_list_columns = None
    filename = None
    transaction_id = None
    deployment_name = 'diabetes regression deployment'
    model_name = 'diabetes regression'
    diabetes_data = datasets.load_diabetes()
    data_df = None
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
        diabetes_X = TestAIOpenScaleClient.diabetes_data.data
        print('sample data records', TestAIOpenScaleClient.diabetes_data.data[1, :].tolist())

        # Split the data into training/testing sets
        diabetes_X_train = diabetes_X[:-20]
        diabetes_X_test = diabetes_X[-20:]

        # Split the targets into training/testing sets
        diabetes_y_train = TestAIOpenScaleClient.diabetes_data.target[:-20]
        diabetes_y_test = TestAIOpenScaleClient.diabetes_data.target[-20:]

        # Create linear regression object
        model = linear_model.LinearRegression()

        # Train the model using the training sets
        model.fit(diabetes_X_train, diabetes_y_train)

        # Make predictions using the testing set
        diabetes_y_pred = model.predict(diabetes_X_test)

        print('predictions', diabetes_y_pred)

        # The coefficients
        print('Coefficients: \n', model.coef_)
        # The mean squared error
        print("Mean squared error: %.2f"
              % mean_squared_error(diabetes_y_test, diabetes_y_pred))
        # Explained variance score: 1 is perfect prediction
        print('Variance score: %.2f' % r2_score(diabetes_y_test, diabetes_y_pred))

        model_meta_props = {
            self.wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
            self.wml_client.repository.ModelMetaNames.NAME: TestAIOpenScaleClient.model_name,
            self.wml_client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: {},
        }

        print("Publishing a new model...")
        published_model_details = self.wml_client.repository.store_model(model=model, meta_props=model_meta_props,
                                                                         training_data=TestAIOpenScaleClient.diabetes_data.data,
                                                                         training_target=TestAIOpenScaleClient.diabetes_data.target)

        print("Published model details:\n{}".format(published_model_details))
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        print("Deploying model: {}, deployment name: {}".format(TestAIOpenScaleClient.model_name, TestAIOpenScaleClient.deployment_name))
        deployment = self.wml_client.deployments.create(artifact_uid=TestAIOpenScaleClient.model_uid, name=TestAIOpenScaleClient.deployment_name, asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        deployment_details = TestAIOpenScaleClient.wml_client.deployments.get_details(self.deployment_uid)
        print("Deployment details:\n{}".format(deployment_details))

    def test_06_subscribe(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(
                source_uid=self.model_uid,
                problem_type=ProblemType.REGRESSION,
                input_data_type=InputDataType.STRUCTURED,
                prediction_column='prediction',
                label_column='l1',
                feature_columns=['f' + str(i) for i in range(0, 10)],
                categorical_columns=[]
            )
        )

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

        payload_scoring = {
            "fields": ['f' + str(i) for i in range(0, 10)],
            "values": [
                [-0.00188201652779104, -0.044641636506989, -0.0514740612388061, -0.0263278347173518,
                 -0.00844872411121698, -0.019163339748222, 0.0744115640787594, -0.0394933828740919, -0.0683297436244215,
                 -0.09220404962683],
                [0.0852989062966783, 0.0506801187398187, 0.0444512133365941, -0.00567061055493425, -0.0455994512826475,
                 -0.0341944659141195, -0.0323559322397657, -0.00259226199818282, 0.00286377051894013,
                 -0.0259303389894746]]
        }

        TestAIOpenScaleClient.payload_scoring = payload_scoring

        for i in range(0, int(TestAIOpenScaleClient.scoring_records)):
            TestAIOpenScaleClient.scoring_result = self.wml_client.deployments.score(scoring_endpoint, payload_scoring)
            print("Scoring result: {}".format(self.scoring_result))
            self.assertIsNotNone(self.scoring_result)

        wait_for_payload_propagation(is_wml_engine=True)

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
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content, scoring_records=self.scoring_records*2)

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        assert_payload_logging_python_table_content(python_table_content=python_table_content, fields=['prediction'])

    def test_14_enable_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.enable(threshold=0.7, min_records=5)

        details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        assert_quality_monitoring_configuration(quality_monitoring_details=details)

    def test_15_feedback_logging(self):
        feedback_records = []
        feedback_record = TestAIOpenScaleClient.diabetes_data.data[1, :].tolist()
        print('feedback_record', feedback_record)
        feedback_record.append(197.61846908)
        print('feedback_record', feedback_record)

        for i in range(0, 2):
            feedback_records.append(feedback_record)

        for j in range(0, 5):
            TestAIOpenScaleClient.subscription.feedback_logging.store(feedback_data=feedback_records)

        print("Waiting 10 seconds for propagation...")
        time.sleep(20)

    def test_16_stats_on_feedback_logging(self):
        TestAIOpenScaleClient.subscription.feedback_logging.show_table()
        TestAIOpenScaleClient.subscription.feedback_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.feedback_logging.describe_table()

    def test_17_run_quality_monitoring(self):
        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run(background_mode=False)
        assert_quality_run(run_details=run_details)
        status = run_details['status']
        self.assertTrue('completed' in status)
        time.sleep(10)

    def test_18_stats_on_quality_monitoring_table(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table(limit=None)
        TestAIOpenScaleClient.subscription.quality_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content()
        quality_metrics = TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue(len(quality_metrics['values']) > 0)

    def test_19_setup_explainability(self):
        columns = ['f' + str(i) for i in range(0, 10)]
        columns.append('l1')
        data = np.concatenate(
            (TestAIOpenScaleClient.diabetes_data.data, TestAIOpenScaleClient.diabetes_data.target[:, None]),
            axis=1)

        TestAIOpenScaleClient.data_df = pd.DataFrame(data=data, columns=columns)

        TestAIOpenScaleClient.subscription.explainability.enable(
            training_data=TestAIOpenScaleClient.data_df
        )

    def test_20_get_details(self):
        details = TestAIOpenScaleClient.subscription.explainability.get_details()
        assert_explainability_configuration(explainability_details=details)

    def test_21_get_transaction_id(self):
        pandas_pd = self.subscription.payload_logging.get_table_content()
        no_payloads = len(pandas_pd['scoring_id'].values)

        # select random record from payload table
        import random
        random_record = random.randint(0, no_payloads-1)
        TestAIOpenScaleClient.transaction_id = pandas_pd['scoring_id'].values[random_record]

        print("Selected trainsaction id: {}".format(self.transaction_id))

    def test_22_run_explainability(self):
        explainability_run = TestAIOpenScaleClient.subscription.explainability.run(
            transaction_id=self.transaction_id,
            background_mode=False
        )
        assert_explainability_run(explainability_run_details=explainability_run)

    def test_22b_list_explanations(self):
        TestAIOpenScaleClient.subscription.explainability.list_explanations()

    def test_23_stats_on_explainability_table(self):
        TestAIOpenScaleClient.subscription.explainability.print_table_schema()
        TestAIOpenScaleClient.subscription.explainability.show_table()
        TestAIOpenScaleClient.subscription.explainability.describe_table()

        pandas_df = TestAIOpenScaleClient.subscription.explainability.get_table_content()
        assert_explainability_pandas_table_content(pandas_table_content=pandas_df)

        python_table_content = TestAIOpenScaleClient.subscription.explainability.get_table_content(format='python')
        assert_explainability_python_table_content(python_table_content=python_table_content)

    def test_24_setup_fairness_monitoring(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.enable(
            features=[
                Feature("f1", majority=[[-0.1, 0.03]], minority=[[0.031, 1]], threshold=0.6)
            ],
            favourable_classes=[[0, 80]],
            unfavourable_classes=[[81, 500]],
            min_records=12,
            training_data=TestAIOpenScaleClient.data_df
        )

    def test_25_get_fairness_monitoring_details(self):
        details = TestAIOpenScaleClient.subscription.fairness_monitoring.get_details()
        assert_fairness_configuration(fairness_monitoring_details=details)

    def test_26_run_fairness(self):
        fairness_run = TestAIOpenScaleClient.subscription.fairness_monitoring.run(background_mode=False)
        assert_fairness_run(fairness_run_details=fairness_run)

    def test_27_stats_on_fairness_monitoring_table(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.fairness_monitoring.show_table()
        TestAIOpenScaleClient.subscription.fairness_monitoring.describe_table()

        pandas_df = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content()
        assert_fairness_monitoring_pandas_table_content(pandas_table_content=pandas_df)

        python_table_content = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content(format='python')
        assert_fairness_monitoring_python_table_content(python_table_content=python_table_content)

    def test_29_disable_all_monitors(self):
        self.subscription.payload_logging.disable()
        self.subscription.performance_monitoring.disable()
        self.subscription.quality_monitoring.disable()
        self.subscription.explainability.disable()
        self.subscription.fairness_monitoring.disable()

        subscription_details = self.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details)

    def test_30_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_31_unbind(self):
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


