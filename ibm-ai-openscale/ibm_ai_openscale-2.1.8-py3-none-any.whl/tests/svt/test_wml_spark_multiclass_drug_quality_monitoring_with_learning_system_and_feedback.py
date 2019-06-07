# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import time
import unittest
from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *


@unittest.skip
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
    quality_monitoring_enabled = False
    scoring_records = None
    db2_service_credentials = None

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
        print(details)
        self.assertTrue(len(json.dumps(details)) > 10)

    def test_03_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_05_prepare_deployment(self):
        model_name = "AIOS Spark Drug learning model 11"
        deployment_name = "AIOS Spark Drug learning deployment 11"

        from pyspark.ml.feature import StringIndexer, IndexToString, VectorAssembler
        from pyspark.ml.classification import DecisionTreeClassifier
        from pyspark.ml.evaluation import MulticlassClassificationEvaluator
        from pyspark.ml import Pipeline

        from pyspark import SparkContext, SQLContext
        ctx = SparkContext.getOrCreate()
        sc = SQLContext(ctx)

        TestAIOpenScaleClient.db2_service_credentials = {
          "port": 50000,
          "db": "BLUDB",
          "username": "dash13173",
          "ssljdbcurl": "jdbc:db2://dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net:50001/BLUDB:sslConnection=true;",
          "host": "dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net",
          "https_url": "https://dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net:8443",
          "dsn": "DATABASE=BLUDB;HOSTNAME=dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=dash13173;PWD=UDoy3w_qT9W_;",
          "hostname": "dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net",
          "jdbcurl": "jdbc:db2://dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net:50000/BLUDB",
          "ssldsn": "DATABASE=BLUDB;HOSTNAME=dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net;PORT=50001;PROTOCOL=TCPIP;UID=dash13173;PWD=UDoy3w_qT9W_;Security=SSL;",
          "uri": "db2://dash13173:UDoy3w_qT9W_@dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net:50000/BLUDB",
          "password": "UDoy3w_qT9W_"
        }
        train_data = sc.read.format("com.databricks.spark.csv").option("header", "true").option("delimiter", ";").option("inferSchema", "true").load(os.path.join(os.curdir, 'datasets', 'drugs', 'drug_feedback_data.csv'))
        test_data = sc.read.format("com.databricks.spark.csv").option("header", "true").option("delimiter", ";").option("inferSchema", "true").load(os.path.join(os.curdir, 'datasets', 'drugs', 'drug_feedback_test.csv'))

        stringIndexer_sex = StringIndexer(inputCol='SEX', outputCol='SEX_IX')
        stringIndexer_bp = StringIndexer(inputCol='BP', outputCol='BP_IX')
        stringIndexer_chol = StringIndexer(inputCol='CHOLESTEROL', outputCol='CHOL_IX')
        stringIndexer_label = StringIndexer(inputCol="DRUG", outputCol="label").fit(train_data)

        vectorAssembler_features = VectorAssembler(inputCols=["AGE", "SEX_IX", "BP_IX", "CHOL_IX", "NA", "K"], outputCol="features")
        dt = DecisionTreeClassifier(labelCol="label", featuresCol="features")
        labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel", labels=stringIndexer_label.labels)
        pipeline_dt = Pipeline(stages=[stringIndexer_label, stringIndexer_sex, stringIndexer_bp, stringIndexer_chol, vectorAssembler_features, dt, labelConverter])

        model = pipeline_dt.fit(train_data)
        predictions = model.transform(test_data)
        evaluatorDT = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
        accuracy = evaluatorDT.evaluate(predictions)

        if "ICP" in get_env():
            training_data_reference = {
                "name": "DRUG feedback",
                "connection": self.database_credentials,
                "source": {
                    "tablename": "DRUG_FEEDBACK_DATA",
                    "type": "dashdb"
                }
            }
        else:
            training_data_reference = {
                "name": "DRUG feedback",
                "connection": self.db2_service_credentials,
                "source": {
                    "tablename": "DRUG_TRAIN_DATA_UPDATED",
                    "type": "dashdb"
                }
            }

        model_props = {
            TestAIOpenScaleClient.wml_client.repository.ModelMetaNames.NAME: "{}".format(model_name),
            TestAIOpenScaleClient.wml_client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: training_data_reference,
            TestAIOpenScaleClient.wml_client.repository.ModelMetaNames.EVALUATION_METHOD: "multiclass",
            TestAIOpenScaleClient.wml_client.repository.ModelMetaNames.EVALUATION_METRICS: [
                {
                    "name": "accuracy",
                    "value": 0.7,
                    "threshold": 0.8
                }
            ]
        }

        wml_models = self.wml_client.repository.get_details()

        for model_in in wml_models['models']['resources']:
            if model_name == model_in['entity']['name']:
                TestAIOpenScaleClient.model_uid = model_in['metadata']['guid']
                break

        if self.model_uid is None:
            print("Storing model ...")

            published_model_details = TestAIOpenScaleClient.wml_client.repository.store_model(model=model, meta_props=model_props, training_data=train_data, pipeline=pipeline_dt)
            TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        wml_deployments = self.wml_client.deployments.get_details()

        for deployment in wml_deployments['resources']:
            if deployment_name == deployment['entity']['name']:
                TestAIOpenScaleClient.deployment_uid = deployment['metadata']['guid']
                break

        if self.deployment_uid is None:
            print("Deploying model...")

            deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name,
                                                            asynchronous=False)
            TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        print("Model details: {}".format(TestAIOpenScaleClient.wml_client.repository.get_details(self.model_uid)))
        print("Model id: {}".format(self.model_uid))
        print("Deployment id: {}".format(self.deployment_uid))

    def test_06_subscribe(self):
        from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType

        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(
            source_uid=TestAIOpenScaleClient.model_uid,
            problem_type=ProblemType.MULTICLASS_CLASSIFICATION,
            input_data_type=InputDataType.STRUCTURED,
            prediction_column='predictedLabel',
            probability_column='probability'
            )
        )

        TestAIOpenScaleClient.aios_model_uid = subscription.uid

    def test_07_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.aios_model_uid)

        subscription_details = self.subscription.get_details()
        print("Subscription details:\n{}".format(subscription_details))

    def test_08_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_09_score(self):

        deployment_details = self.wml_client.deployments.get_details(TestAIOpenScaleClient.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        payload_scoring = SparkBestHeartDrug.get_scoring_payload_from_training_data()

        scores = None
        TestAIOpenScaleClient.scoring_records = 20
        for i in range(0, self.scoring_records):
            scores = self.wml_client.deployments.score(scoring_endpoint, payload_scoring)

        self.assertIsNotNone(scores)
        print('Scoring result: {}'.format(scores))

        wait_for_payload_propagation(is_wml_engine=True)

    def test_10_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        self.subscription.payload_logging.show_table()
        self.subscription.payload_logging.describe_table()

        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content, scoring_records=self.scoring_records)

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        assert_payload_logging_python_table_content(python_table_content=python_table_content, fields=['prediction', 'probability'])

    def test_11_setup_quality_monitoring(self):
        try:
            TestAIOpenScaleClient.subscription.quality_monitoring.enable(threshold=0.8, min_records=5)
            TestAIOpenScaleClient.quality_monitoring_enabled = True
        except Exception as ex:
            TestAIOpenScaleClient.quality_monitoring_enabled = False
            print(ex)

    def test_12_get_quality_monitoring_details(self):
        accuracy_details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        self.assertTrue('location' in str(accuracy_details))

    def test_13_send_feedback_data(self):
        if not self.quality_monitoring_enabled:
            self.skipTest("Quality monitoring is not enabled.")

        TestAIOpenScaleClient.subscription.feedback_logging.store(
            [
                [74.0, 'M', 'HIGH', 'HIGH', 0.715337, 0.074773, 'drugB'],
                [58.0, 'F', 'HIGH', 'NORMAL', 0.868924, 0.061023, 'drugB'],
                [68.0, 'F', 'HIGH', 'NORMAL', 0.77541, 0.0761, 'drugB'],
                [65.0, 'M', 'HIGH', 'NORMAL', 0.635551, 0.056043, 'drugB'],
                [60.0, 'F', 'HIGH', 'HIGH', 0.800607, 0.060181, 'drugB'],
                [70.0, 'M', 'HIGH', 'HIGH', 0.658606, 0.047153, 'drugB'],
                [60.0, 'M', 'HIGH', 'HIGH', 0.805651, 0.057821, 'drugB'],
                [59.0, 'M', 'HIGH', 'HIGH', 0.816356, 0.058583, 'drugB']
            ],
            fields=['AGE', 'SEX', 'BP', 'CHOLESTEROL', 'NA', 'K', 'DRUG']
        )

    def test_14_set_learning_system(self):
        if not self.quality_monitoring_enabled:
            self.skipTest("Quality monitoring is not enabled.")


        feedback_data_reference = {
            "name": "DRUG feedback",
            "connection": self.db2_service_credentials,
            "source": {
                "tablename": "DRUG_FEEDBACK_DATA_2",
                "type": "dashdb"
            }
        }


        # accuracy_details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        # feedback_data_reference = accuracy_details['parameters']['feedback_data_reference']
        # feedback_data_reference['location']['tablename'] = feedback_data_reference['location']['table_name']

        spark_credentials = get_spark_reference()

        system_config = {
            TestAIOpenScaleClient.wml_client.learning_system.ConfigurationMetaNames.FEEDBACK_DATA_REFERENCE: feedback_data_reference,
            TestAIOpenScaleClient.wml_client.learning_system.ConfigurationMetaNames.MIN_FEEDBACK_DATA_SIZE: 5,
            TestAIOpenScaleClient.wml_client.learning_system.ConfigurationMetaNames.SPARK_REFERENCE: spark_credentials,
            TestAIOpenScaleClient.wml_client.learning_system.ConfigurationMetaNames.AUTO_RETRAIN: "conditionally",
            TestAIOpenScaleClient.wml_client.learning_system.ConfigurationMetaNames.AUTO_REDEPLOY: "always"
        }

        learning_system_config = TestAIOpenScaleClient.wml_client.learning_system.setup(model_uid=TestAIOpenScaleClient.model_uid, meta_props=system_config)
        print(learning_system_config)
        self.assertTrue('tablename' in str(learning_system_config))

    def test_15_run_learning_iteration(self):
        if not self.quality_monitoring_enabled:
            self.skipTest("Quality monitoring is not enabled.")

        run_details = TestAIOpenScaleClient.wml_client.learning_system.run(TestAIOpenScaleClient.model_uid, asynchronous=False)
        print(run_details)
        import time
        time.sleep(10)
        self.assertTrue(run_details['entity']['status']['state'] == 'COMPLETED')
        TestAIOpenScaleClient.wml_client.learning_system.list_metrics(TestAIOpenScaleClient.model_uid)

    def test_16_stats_on_quality_monitoring_table(self):
        if not self.quality_monitoring_enabled:
            self.skipTest("Quality monitoring is not enabled.")

        TestAIOpenScaleClient.subscription.quality_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content()
        quality_metrics = TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue(len(quality_metrics['values']) > 0)

    def test_17_stats_on_feedback_logging_table(self):
        if not self.quality_monitoring_enabled:
            self.skipTest("Quality monitoring is not enabled.")

        TestAIOpenScaleClient.subscription.feedback_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.feedback_logging.show_table()
        TestAIOpenScaleClient.subscription.feedback_logging.describe_table()
        TestAIOpenScaleClient.subscription.feedback_logging.get_table_content()

    def test_18_disable_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.disable()

    def test_19_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_20_unbind(self):
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
