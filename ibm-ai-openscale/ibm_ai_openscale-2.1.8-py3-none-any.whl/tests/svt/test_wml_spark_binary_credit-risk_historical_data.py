# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from pyspark import SparkContext, SQLContext
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler, IndexToString
from pyspark.sql.types import StructType, DoubleType, StringType, ArrayType

from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes import Feature
from ibm_ai_openscale.supporting_classes.measurement_record import MeasurementRecord
from ibm_ai_openscale.supporting_classes.enums import InputDataType, ProblemType
from preparation_and_cleaning import *


class TestAIOpenScaleClient(unittest.TestCase):
    transaction_id = None
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

    scoring_records = 0
    feedback_records = 0

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

    def test_05_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        print("Binding details:\n{}".format(self.ai_client.data_mart.bindings.get_details(self.binding_uid)))

        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_06_prepare_model(self):
        asset_name = "AIOS Spark German Risk model"
        deployment_name = "AIOS Spark German Risk deployment"

        ctx = SparkContext.getOrCreate()
        sc = SQLContext(ctx)

        spark_df = sc.read.format("com.databricks.spark.csv").option("header", "true").option("delimiter", ",").option("inferSchema", "true").load(
            os.path.join(os.curdir, 'datasets', 'German_credit_risk', 'credit_risk_training.csv'))
        spark_df.printSchema()

        (train_data, test_data) = spark_df.randomSplit([0.8, 0.2], 24)
        print("Number of records for training: " + str(train_data.count()))
        print("Number of records for evaluation: " + str(test_data.count()))

        si_CheckingStatus = StringIndexer(inputCol='CheckingStatus', outputCol='CheckingStatus_IX')
        si_CreditHistory = StringIndexer(inputCol='CreditHistory', outputCol='CreditHistory_IX')
        si_LoanPurpose = StringIndexer(inputCol='LoanPurpose', outputCol='LoanPurpose_IX')
        si_ExistingSavings = StringIndexer(inputCol='ExistingSavings', outputCol='ExistingSavings_IX')
        si_EmploymentDuration = StringIndexer(inputCol='EmploymentDuration', outputCol='EmploymentDuration_IX')
        si_Sex = StringIndexer(inputCol='Sex', outputCol='Sex_IX')
        si_OthersOnLoan = StringIndexer(inputCol='OthersOnLoan', outputCol='OthersOnLoan_IX')
        si_OwnsProperty = StringIndexer(inputCol='OwnsProperty', outputCol='OwnsProperty_IX')
        si_InstallmentPlans = StringIndexer(inputCol='InstallmentPlans', outputCol='InstallmentPlans_IX')
        si_Housing = StringIndexer(inputCol='Housing', outputCol='Housing_IX')
        si_Job = StringIndexer(inputCol='Job', outputCol='Job_IX')
        si_Telephone = StringIndexer(inputCol='Telephone', outputCol='Telephone_IX')
        si_ForeignWorker = StringIndexer(inputCol='ForeignWorker', outputCol='ForeignWorker_IX')
        si_Label = StringIndexer(inputCol="Risk", outputCol="label").fit(spark_df)
        label_converter = IndexToString(inputCol="prediction", outputCol="predictedLabel", labels=si_Label.labels)

        va_features = VectorAssembler(
            inputCols=["CheckingStatus_IX", "CreditHistory_IX", "LoanPurpose_IX", "ExistingSavings_IX",
                       "EmploymentDuration_IX", "Sex_IX", "OthersOnLoan_IX", "OwnsProperty_IX", "InstallmentPlans_IX",
                       "Housing_IX", "Job_IX", "Telephone_IX", "ForeignWorker_IX", "LoanDuration", "LoanAmount",
                       "InstallmentPercent", "CurrentResidenceDuration", "LoanDuration", "Age", "ExistingCreditsCount",
                       "Dependents"], outputCol="features")

        classifier = RandomForestClassifier(featuresCol="features")

        pipeline = Pipeline(
            stages=[si_CheckingStatus, si_CreditHistory, si_EmploymentDuration, si_ExistingSavings, si_ForeignWorker,
                    si_Housing, si_InstallmentPlans, si_Job, si_LoanPurpose, si_OthersOnLoan,
                    si_OwnsProperty, si_Sex, si_Telephone, si_Label, va_features, classifier, label_converter])

        model = pipeline.fit(train_data)
        predictions = model.transform(test_data)
        evaluator = BinaryClassificationEvaluator(rawPredictionCol="prediction")
        auc = evaluator.evaluate(predictions)

        print("Accuracy = %g" % auc)

        train_data_schema = spark_df.schema
        label_field = next(f for f in train_data_schema.fields if f.name == "Risk")
        label_field.metadata['values'] = si_Label.labels
        input_fileds = filter(lambda f: f.name != "Risk", train_data_schema.fields)

        output_data_schema = StructType(list(input_fileds)). \
            add("prediction", DoubleType(), True, {'modeling_role': 'prediction'}). \
            add("predictedLabel", StringType(), True,
                {'modeling_role': 'decoded-target', 'values': si_Label.labels}). \
            add("probability", ArrayType(DoubleType()), True, {'modeling_role': 'probability'})

        if "ICP" in get_env():
            training_data_reference = {
                "name": "Credit Risk feedback",
                "connection": self.database_credentials,
                "source": {
                    "tablename": "TRAININGDATA.CREDIT_RISK_TRAINING",
                    "type": "dashdb"
                }
            }
        else:
            db2_credentials = {
                "hostname": "dashdb-entry-yp-dal09-10.services.dal.bluemix.net",
                "password": "89TsmoAN_Sb_",
                "https_url": "https://dashdb-entry-yp-dal09-10.services.dal.bluemix.net:8443",
                "port": 50000,
                "ssldsn": "DATABASE=BLUDB;HOSTNAME=dashdb-entry-yp-dal09-10.services.dal.bluemix.net;PORT=50001;PROTOCOL=TCPIP;UID=dash14647;PWD=89TsmoAN_Sb_;Security=SSL;",
                "host": "dashdb-entry-yp-dal09-10.services.dal.bluemix.net",
                "jdbcurl": "jdbc:db2://dashdb-entry-yp-dal09-10.services.dal.bluemix.net:50000/BLUDB",
                "uri": "db2://dash14647:89TsmoAN_Sb_@dashdb-entry-yp-dal09-10.services.dal.bluemix.net:50000/BLUDB",
                "db": "BLUDB",
                "dsn": "DATABASE=BLUDB;HOSTNAME=dashdb-entry-yp-dal09-10.services.dal.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=dash14647;PWD=89TsmoAN_Sb_;",
                "username": "dash14647",
                "ssljdbcurl": "jdbc:db2://dashdb-entry-yp-dal09-10.services.dal.bluemix.net:50001/BLUDB:sslConnection=true;"
            }

            training_data_reference = {
                "name": "Credit Risk feedback",
                "connection": db2_credentials,
                "source": {
                    "tablename": "CREDIT_RISK_TRAINING",
                    "type": "dashdb"
                }
            }

        model_props = {
            self.wml_client.repository.ModelMetaNames.NAME: "{}".format(asset_name),
            self.wml_client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: training_data_reference,
            self.wml_client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA: output_data_schema.jsonValue(),
            self.wml_client.repository.ModelMetaNames.EVALUATION_METRICS: [
                {
                    "name": "AUC",
                    "value": auc,
                    "threshold": 0.8
                }
            ]
        }

        print("Publishing a new model...")
        published_model_details = self.wml_client.repository.store_model(model=model, meta_props=model_props, training_data=train_data, pipeline=pipeline)

        print("Published model details:\n{}".format(published_model_details))
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        print("Deploying model: {}, deployment name: {}".format(asset_name, deployment_name))
        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name, asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        print("Deployment details:\n{}".format(deployment_details))

    def test_07_subscribe(self):
        # get_details_from_restapi(ai_client=self.ai_client, binding_uid=self.binding_uid)

        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(
            source_uid=TestAIOpenScaleClient.model_uid,
            binding_uid=self.binding_uid,
            problem_type=ProblemType.BINARY_CLASSIFICATION,
            input_data_type=InputDataType.STRUCTURED,
            prediction_column='predictedLabel',
            probability_column='probability',
            feature_columns=['CheckingStatus', 'LoanDuration', 'CreditHistory', 'LoanPurpose', 'LoanAmount',
                             'ExistingSavings', 'EmploymentDuration', 'InstallmentPercent', 'Sex', 'OthersOnLoan',
                             'CurrentResidenceDuration', 'OwnsProperty', 'Age', 'InstallmentPlans', 'Housing',
                             'ExistingCreditsCount', 'Job', 'Dependents', 'Telephone', 'ForeignWorker'],
            categorical_columns=['CheckingStatus', 'CreditHistory', 'LoanPurpose', 'ExistingSavings',
                                 'EmploymentDuration', 'Sex', 'OthersOnLoan', 'OwnsProperty', 'InstallmentPlans',
                                 'Housing', 'Job', 'Telephone', 'ForeignWorker']
        ))

        TestAIOpenScaleClient.subscription_uid = subscription.uid
        TestAIOpenScaleClient.subscription = subscription

        print("Subscription details: {}".format(subscription.get_details()))

    def test_09_score(self):
        deployment_details = self.wml_client.deployments.get_details(TestAIOpenScaleClient.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        fields = ["CheckingStatus", "LoanDuration", "CreditHistory", "LoanPurpose", "LoanAmount", "ExistingSavings",
                  "EmploymentDuration", "InstallmentPercent", "Sex", "OthersOnLoan", "CurrentResidenceDuration",
                  "OwnsProperty", "Age", "InstallmentPlans", "Housing", "ExistingCreditsCount", "Job", "Dependents",
                  "Telephone", "ForeignWorker"]
        values = [
            ["no_checking", 33, "outstanding_credit", "appliances", 5696, "unknown", "greater_7", 4, "male",
             "co-applicant", 4, "unknown", 54, "none", "free", 2, "skilled", 1, "yes", "yes"],
            ["0_to_200", 13, "prior_payments_delayed", "retraining", 1375, "100_to_500", "4_to_7", 3, "male", "none", 3,
             "real_estate", 37, "none", "own", 2, "management_self-employed", 1, "none", "yes"]
        ]

        payload_scoring = {"fields": fields, "values": values}
        print("Scoring payload: {}".format(payload_scoring))

        TestAIOpenScaleClient.scoring_records = 6
        for i in range(0, int(self.scoring_records/2)):
            scorings = self.wml_client.deployments.score(scoring_endpoint, payload_scoring)
            self.assertIsNotNone(scorings)

        print("Scoring output: {}".format(scorings))
        print("Waiting 20 seconds for propagation.")
        time.sleep(20)

    def test_10_stats_on_payload_logging_table(self):
        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        assert_payload_logging_python_table_content(python_table_content=python_table_content, fields=['prediction', 'probability'])

    def test_11_setup_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.enable(threshold=0.8, min_records=5)

    def test_12_setup_fairness_monitoring(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.enable(
            features=[
                Feature("Sex", majority=['male'], minority=['female'], threshold=0.95),
                Feature("Age", majority=[[26, 75]], minority=[[18, 25]], threshold=0.95)
            ],
            favourable_classes=['No Risk'],
            unfavourable_classes=['Risk'],
            min_records=4,
        )

    def test_13_inject_quality_metrics(self):
        quality_metric = {'area_under_roc': 0.666}
        TestAIOpenScaleClient.subscription.monitoring.store_metrics(monitor_uid='quality', metrics=quality_metric)

        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.monitoring.show_table(monitor_uid='quality')

        quality_metrics_py = self.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue('0.666' in str(quality_metrics_py))

    def test_14_inject_quality_measurements(self):
        quality_metric = {'area_under_roc': 0.999}
        source = {
            "id": "confusion_matrix_1",
            "type": "confusion_matrix",
            "data": {
                "labels": ["Risk", "No Risk"],
                "values": [[11, 21],
                           [20, 10]]}
        }

        measurements = [
            MeasurementRecord(metrics=quality_metric, sources=source),
            MeasurementRecord(metrics=quality_metric, sources=source)
        ]

        details = TestAIOpenScaleClient.subscription.monitoring.store_measurements(monitor_uid='quality', measurements=measurements)
        print('Measurement details', details)

        measurement_id = details[0]['measurement_id']

        print('measurement_id', measurement_id)
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_confusion_matrix(measurement_id=measurement_id)

        quality_metrics_py = self.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue(str(quality_metric['area_under_roc']) in str(quality_metrics_py))
        self.assertTrue('20' in str(quality_metrics_py))

        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.monitoring.show_table(monitor_uid='quality')

    def test_15_inject_performance_metrics(self):
        if "ICP" in get_env():
            self.skipTest("Performance monitoring is not working on ICP with WML scoring.")

        performance_metric = {'records': 245, 'response_time': 62.33809845686894}
        TestAIOpenScaleClient.subscription.monitoring.store_metrics(monitor_uid='performance', metrics=performance_metric)

        self.subscription.performance_monitoring.show_table()

        performance_table_python = self.subscription.performance_monitoring.get_table_content(format='python')
        self.assertTrue('62.33809845686894' in str(performance_table_python))

    def test_16_inject_performance_measurements(self):
        if "ICP" in get_env():
            self.skipTest("Performance monitoring is not working on ICP with WML scoring.")

        measurements = [
            MeasurementRecord(metrics={'records': 245, 'response_time': 62.33809845686894}),
            MeasurementRecord(metrics={'records': 45, 'response_time': 2.33809845686894})
        ]

        details = TestAIOpenScaleClient.subscription.monitoring.store_measurements(monitor_uid='performance',
                                                                               measurements=measurements)
        self.assertTrue('2.33809845686894' in str(details))

    def test_17_inject_fairness_metrics(self):
        fairness_metric = {'metrics': [{'feature': 'Sex', 'majority': {'values': [{'value': 'male', 'distribution': {'male': [{'count': 65, 'label': 'No Risk', 'is_favourable': True}, {'count': 4, 'label': 'Risk', 'is_favourable': False}]}, 'fav_class_percent': 95.0}], 'total_fav_percent': 95.0, 'total_rows_percent': 33.33333333333333}, 'minority': {'values': [{'value': 'female', 'is_biased': True, 'distribution': {'female': [{'count': 29, 'label': 'No Risk', 'is_favourable': True}, {'count': 2, 'label': 'Risk', 'is_favourable': False}]}, 'fairness_value': 0.947333, 'fav_class_percent': 90.0}], 'total_fav_percent': 90.0, 'total_rows_percent': 33.33333333333333}}, {'feature': 'Age', 'majority': {'values': [{'value': [26, 75], 'distribution': {'26': [{'count': 4, 'label': 'No Risk', 'is_favourable': True}], '28': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '29': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '30': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '31': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '32': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '33': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '34': [{'count': 1, 'label': 'Risk', 'is_favourable': False}, {'count': 4, 'label': 'No Risk', 'is_favourable': True}], '35': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '36': [{'count': 3, 'label': 'No Risk', 'is_favourable': True}], '37': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '38': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '39': [{'count': 3, 'label': 'No Risk', 'is_favourable': True}, {'count': 1, 'label': 'Risk', 'is_favourable': False}], '40': [{'count': 3, 'label': 'No Risk', 'is_favourable': True}], '41': [{'count': 3, 'label': 'No Risk', 'is_favourable': True}], '43': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '45': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '47': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '49': [{'count': 1, 'label': 'Risk', 'is_favourable': False}], '50': [{'count': 3, 'label': 'No Risk', 'is_favourable': True}, {'count': 1, 'label': 'Risk', 'is_favourable': False}], '52': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '54': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '55': [{'count': 1, 'label': 'Risk', 'is_favourable': False}, {'count': 1, 'label': 'No Risk', 'is_favourable': True}], '71': [{'count': 1, 'label': 'Risk', 'is_favourable': False}]}, 'fav_class_percent': 88.43537414965986}], 'total_fav_percent': 88.43537414965986, 'total_rows_percent': 49.0}, 'minority': {'values': [{'value': [18, 25], 'is_biased': False, 'distribution': {'19': [{'count': 16, 'label': 'No Risk', 'is_favourable': True}], '20': [{'count': 16, 'label': 'No Risk', 'is_favourable': True}], '21': [{'count': 11, 'label': 'No Risk', 'is_favourable': True}], '23': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '24': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '25': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}]}, 'fairness_value': 1.101, 'fav_class_percent': 97.38562091503267}], 'total_fav_percent': 97.38562091503267, 'total_rows_percent': 51.0}, 'bias_source': {'values': []}}], 'score_type': 'desperate impact', 'response_time': '13.128683', 'rows_analyzed': 100, 'perturbed_data_size': 200, 'manual_labelling_store': 'Manual_Labeling_dd79dd1b-0afc-436e-9999-6fd6414f81c2'}
        TestAIOpenScaleClient.subscription.monitoring.store_metrics(monitor_uid='fairness', metrics=fairness_metric)

        TestAIOpenScaleClient.subscription.fairness_monitoring.show_table()

        python_table_content = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content(format='python')
        self.assertTrue('0.947333' in str(python_table_content))

    def test_19_inject_debias_metrics(self):
        debiased_fairness_metric = {'metrics': [{'feature': 'Sex', 'majority': {'values': [{'value': 'male', 'distribution': {'male': [{'count': 5, 'label': 'Risk', 'is_favourable': False}, {'count': 56, 'label': 'No Risk', 'is_favourable': False}]}, 'fav_class_percent': 95.0}], 'total_fav_percent': 95.0, 'total_rows_percent': 50.0}, 'minority': {'values': [{'value': 'female', 'is_biased': False, 'distribution': {'female': [{'count': 39, 'label': 'No Risk', 'is_favourable': False}]}, 'fairness_value': 1.0, 'fav_class_percent': 95.0}], 'total_fav_percent': 95.0, 'total_rows_percent': 50.0}}, {'feature': 'Age', 'majority': {'values': [{'value': [26, 75], 'distribution': {'26': [{'count': 2, 'label': 'No Risk', 'is_favourable': False}], '28': [{'count': 5, 'label': 'No Risk', 'is_favourable': False}], '29': [{'count': 2, 'label': 'No Risk', 'is_favourable': False}], '30': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '31': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '32': [{'count': 4, 'label': 'No Risk', 'is_favourable': False}], '34': [{'count': 4, 'label': 'No Risk', 'is_favourable': False}], '35': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '36': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '37': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '39': [{'count': 2, 'label': 'No Risk', 'is_favourable': False}], '40': [{'count': 2, 'label': 'No Risk', 'is_favourable': False}], '41': [{'count': 2, 'label': 'No Risk', 'is_favourable': False}], '42': [{'count': 1, 'label': 'Risk', 'is_favourable': False}], '43': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '44': [{'count': 3, 'label': 'No Risk', 'is_favourable': False}], '45': [{'count': 2, 'label': 'No Risk', 'is_favourable': False}], '48': [{'count': 2, 'label': 'No Risk', 'is_favourable': False}], '49': [{'count': 1, 'label': 'Risk', 'is_favourable': False}], '52': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '59': [{'count': 1, 'label': 'Risk', 'is_favourable': False}], '60': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '66': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '67': [{'count': 1, 'label': 'Risk', 'is_favourable': False}]}, 'fav_class_percent': 96.17834394904459}], 'total_fav_percent': 96.17834394904459, 'total_rows_percent': 78.5}, 'minority': {'values': [{'value': [18, 25], 'is_biased': True, 'distribution': {'19': [{'count': 17, 'label': 'No Risk', 'is_favourable': False}], '20': [{'count': 18, 'label': 'No Risk', 'is_favourable': False}, {'count': 1, 'label': 'Risk', 'is_favourable': False}], '21': [{'count': 13, 'label': 'No Risk', 'is_favourable': False}], '22': [{'count': 4, 'label': 'No Risk', 'is_favourable': False}], '23': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '24': [{'count': 1, 'label': 'No Risk', 'is_favourable': False}], '25': [{'count': 2, 'label': 'No Risk', 'is_favourable': False}]}, 'fairness_value': 0.974, 'fav_class_percent': 93.7062937062937}], 'total_fav_percent': 93.7062937062937, 'total_rows_percent': 71.5}, 'bias_source': {'values': [{'range': '[18,19]', 'fav_percent': 88.23529411764706}]}}], 'debiased': True, 'score_type': 'desperate impact', 'response_time': '237.744371', 'rows_analyzed': 100, 'perturbed_data_size': 100, 'manual_labelling_store': 'Manual_Labeling_dd79dd1b-0afc-436e-9999-6fd6414f81c2'}
        TestAIOpenScaleClient.subscription.monitoring.store_metrics(monitor_uid='debiased_fairness',                                                                    metrics=debiased_fairness_metric)

    def test_20_get_metrics(self):
        print("Old metrics:")
        print(self.ai_client.data_mart.get_deployment_metrics())
        print(self.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(self.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(self.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))

        ### BINARY CHECK

        metrics = {
            'area_under_roc': None,
        }

        quality_metrics = self.ai_client.data_mart.get_deployment_metrics(metric_type='quality')
        print("Old quality metric:\n{}".format(quality_metrics))

        for metric in quality_metrics['deployment_metrics'][0]['metrics'][0]['value']['metrics']:
            if metric['name'] in metrics.keys():
                metrics[metric['name']] = metric['value']

        ootb_quality_metrics = self.subscription.quality_monitoring.get_metrics()
        print("New quality metrics:\n{}".format(ootb_quality_metrics))

        for metric in ootb_quality_metrics[0]['metrics']:
            if metric['id'] in metrics.keys():
                print("Comparing metrics: {}".format(metric['id']))
                self.assertEqual(metric['value'], metrics[metric['id']],
                                 msg="metric {} has different value in ootb api".format(metric['id']))

        print(self.subscription.quality_monitoring.get_metrics(format="samples"))

    def test_21_insert_quality_historical_records(self):
        import json
        from ibm_ai_openscale.utils import generate_historical_timestamps

        data_path = os.path.join(os.curdir, 'datasets', 'German_credit_risk', 'historical_records', 'credit_risk_quality_measurements.json')

        with open(data_path) as json_file:
            records = json.load(json_file)

        history_days = int(len(records)/24)
        timestamps = generate_historical_timestamps(days=history_days)
        measurements = []

        for record, timestamp in zip(records, timestamps):
            measurements.append(
                MeasurementRecord(
                    metrics=record['metrics'],
                    sources=record['sources'],
                    timestamp=timestamp))

        details = TestAIOpenScaleClient.subscription.monitoring.store_measurements(
            monitor_uid='quality',
            measurements=measurements)

        print('Data insert details', details)
        self.assertTrue('0.7485207100591716' in str(details))

    def test_33_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_34_unbind(self):
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
