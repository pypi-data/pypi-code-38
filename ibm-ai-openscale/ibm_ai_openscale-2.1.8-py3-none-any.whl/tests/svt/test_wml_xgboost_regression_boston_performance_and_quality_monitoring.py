from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType, FeedbackFormat
from preparation_and_cleaning import *
from sklearn.datasets import load_boston
import pandas as pd


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
    feedback_records = None
    boston_dataset = load_boston()
    start_date = datetime.utcnow().isoformat() + "Z"

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
        assert_datamart_details(details, schema=self.schema, state='active')

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
        import xgboost as xgb
        from sklearn.model_selection import train_test_split

        asset_name = "AIOS Xgboost Boston House Model"
        deployment_name = "AIOS Xgboost Boston House Deployment"

        model_meta_props = {
            self.wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
            self.wml_client.repository.ModelMetaNames.NAME: asset_name,
            self.wml_client.repository.ModelMetaNames.FRAMEWORK_NAME: "xgboost",
            self.wml_client.repository.ModelMetaNames.FRAMEWORK_VERSION: "0.8",
        }


        data = pd.DataFrame(self.boston_dataset.data)
        data.columns = self.boston_dataset.feature_names
        X, y = data.iloc[:, :-1], data.iloc[:, -1]
        data_dmatrix = xgb.DMatrix(data=X, label=y)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)
        xg_reg = xgb.XGBRegressor(objective='reg:linear', colsample_bytree=0.3, learning_rate=0.1, max_depth=5,
                                  alpha=10, n_estimators=10)

        xg_reg.fit(X_train, y_train)

        # preds = xg_reg.predict(X_test)
        # print(preds)
        #
        # bst = xgb.XGBRegressor()
        # bst.load_model("artifacts/XGboost/boston-house-xgboost.model")

        print("Publishing a new model...")
        published_model_details = self.wml_client.repository.store_model(model=xg_reg, meta_props=model_meta_props)

        print("Published model details:\n{}".format(published_model_details))
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        print("Deploying model: {}, deployment name: {}".format(asset_name, deployment_name))
        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name, asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        print("Deployment details:\n{}".format(deployment_details))

    def test_06_subscribe(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(
                source_uid=self.model_uid,
                binding_uid=self.binding_uid,
                problem_type=ProblemType.REGRESSION,
                input_data_type=InputDataType.STRUCTURED,
                prediction_column='prediction',
                label_column='LSTAT'
            )
        )
        self.assertIsNotNone(self.subscription)
        TestAIOpenScaleClient.subscription_uid = self.subscription.uid

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
        assert_payload_logging_configuration(payload_logging_details=payload_logging_details, dynamic_schema_update=True)

    def test_10_get_performance_monitoring_details(self):
        performance_monitoring_details = self.subscription.performance_monitoring.get_details()
        assert_performance_monitoring_configuration(performance_monitoring_details=performance_monitoring_details)

    def test_11_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)
        fields = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 'TAX', 'PTRATIO', 'B']

        scoring_payload = {
            'fields': fields,
            'values': [
                [51.1358, 0.0, 18.1, 0.0, 0.597, 5.757, 100.0, 1.413, 24.0, 666.0, 20.2, 2.6],
                [12.0482, 0.0, 18.1, 0.0, 0.614, 5.648, 87.6, 1.9512, 24.0, 666.0, 20.2, 291.55]
            ]
        }
        print("Scoring payload:\n{}".format(scoring_payload))

        scoring_result = None
        TestAIOpenScaleClient.scoring_records = 20
        for i in range(0, int(self.scoring_records/2)):
            scoring_result = self.wml_client.deployments.score(scoring_endpoint, scoring_payload)

        self.assertIsNotNone(scoring_result)
        print("Scoring result: {}".format(scoring_result))

        wait_for_payload_propagation(is_wml_engine=True)

    def test_12_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        self.subscription.payload_logging.show_table()
        self.subscription.payload_logging.describe_table()

        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content, scoring_records=self.scoring_records)

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        assert_payload_logging_python_table_content(python_table_content=python_table_content, fields=['CRIM', 'prediction'])

    def test_13_payload_logging_data_distribution(self):
        end_date = datetime.utcnow().isoformat() + "Z"
        data_distribution_run = TestAIOpenScaleClient.subscription.payload_logging.data_distribution.run(
            start_date=self.start_date,
            end_date=end_date,
            group=['AGE'],
            agg=['AGE:avg'],
            background_mode=False)

        run_id = data_distribution_run['id']
        data_distribution = self.subscription.payload_logging.data_distribution.get_run_result(run_id=run_id)
        print('Payload data distribution')
        print(data_distribution)

        self.assertEqual(data_distribution.shape[0], 1)
        self.assertEqual(data_distribution.shape[1], 2)
        data_columns = data_distribution.columns.values
        self.assertIn("AGE", data_columns)
        self.assertIn("AGE:avg", data_columns)

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
        TestAIOpenScaleClient.feedback_records = 50

        data = pd.DataFrame(self.boston_dataset.data)
        data.columns = self.boston_dataset.feature_names

        self.subscription.feedback_logging.store(
            feedback_data=data.sample(n=self.feedback_records).to_csv(index=False),
            feedback_format=FeedbackFormat.CSV,
            data_header=True,
            data_delimiter=',')

        print("Waiting 30 seconds for propagation.")
        time.sleep(30)

    def test_17_stats_on_feedback_logging(self):
        self.subscription.feedback_logging.show_table()
        self.subscription.feedback_logging.print_table_schema()
        self.subscription.feedback_logging.describe_table()

        feedback_pd = self.subscription.feedback_logging.get_table_content(format='pandas')
        assert_feedback_pandas_table_content(pandas_table_content=feedback_pd, feedback_records=self.feedback_records)

    def test_18_feedback_logging_data_distribution(self):
        end_date = datetime.utcnow().isoformat() + "Z"
        feedback_distribution_run = TestAIOpenScaleClient.subscription.feedback_logging.data_distribution.run(
            start_date=TestAIOpenScaleClient.start_date,
            end_date=end_date,
            group=['ZN', 'RAD'],
            agg=['count', 'INDUS:max'],
            filter=['AGE:gt:60', 'TAX:lte:500'])

        run_id = feedback_distribution_run['id']
        feedback_distribution = self.subscription.feedback_logging.data_distribution.get_run_result(run_id=run_id)
        print("Feedback data distribution:")
        print(feedback_distribution)

        self.assertGreater(feedback_distribution.shape[0], 1)
        self.assertEqual(feedback_distribution.shape[1], 4)

    def test_19_run_quality_monitoring(self):
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

    def test_20_stats_on_quality_monitoring_table(self):
        self.subscription.quality_monitoring.print_table_schema()
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_table(limit=None)
        self.subscription.quality_monitoring.describe_table()

        quality_monitoring_table = self.subscription.quality_monitoring.get_table_content()
        assert_quality_monitoring_pandas_table_content(pandas_table_content=quality_monitoring_table)

        quality_metrics = self.subscription.quality_monitoring.get_table_content(format='python')
        assert_quality_monitoring_python_table_content(python_table_content=quality_metrics)

    def test_21_get_metrics(self):
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
                self.assertEqual(metric['value'], metrics[metric['id']],
                                 msg="metric {} has different value in ootb api".format(metric['id']))
                if 'lower_limit' in metric.keys():
                    self.assertEqual(metric['lower_limit'], metrics['threshold'],
                                     msg="lower_limit is not the same as threshold!")

        print(self.subscription.quality_monitoring.get_metrics(format="samples"))

    def test_22_disable_monitors(self):
        self.subscription.payload_logging.disable()
        self.subscription.performance_monitoring.disable()
        self.subscription.quality_monitoring.disable()

        subscription_details = self.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details)

    def test_23_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_24_unbind(self):
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
