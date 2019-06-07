# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import unittest

from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *
from pyspark import SparkContext, SQLContext
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler, IndexToString
from pyspark.sql.types import StructType, DoubleType, StringType, ArrayType


@unittest.skipIf("ICP" in get_env(), "Disabled on ICP...")
class TestAIOpenScaleClient(unittest.TestCase):
    binding_uid = None
    deployment_uid = None
    model_uid = None
    aios_model_uid = None
    scoring_url = None
    labels = None
    ai_client = None
    wml_client = None
    subscription = None
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

    def test_02_delete_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.delete()
        if "ICP" in get_env():
            if "bluemix.net" in str(self.database_credentials):
                clean_db2_schema(self.database_credentials, self.schema)
            else:
                clean_db2_icp_schema(self.database_credentials, self.schema)
        else:
            if 'postgres' in str(self.database_credentials):
                delete_schema(self.database_credentials, self.schema)
                create_schema(self.database_credentials, self.schema)
            elif 'db2' in str(self.database_credentials):
                clean_db2_schema(self.database_credentials, self.schema)

    def test_03_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_04_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))
        self.assertIsNotNone(self.binding_uid)

    def test_05_unbind(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.delete(TestAIOpenScaleClient.binding_uid)
        TestAIOpenScaleClient.binding_uid = None

    def test_06_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML second instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML second instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))
        self.assertIsNotNone(self.binding_uid)

    def test_07_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        print("Binding id: {}".format(binding_uid))
        self.assertEqual(binding_uid, TestAIOpenScaleClient.binding_uid)

        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)
        self.assertIsNotNone(TestAIOpenScaleClient.wml_client)

    def test_08_prepare_deployment(self):
        asset_name = "AIOS Spark German Risk model"
        deployment_name = "AIOS Spark German Risk deployment"

        ctx = SparkContext.getOrCreate()
        sc = SQLContext(ctx)

        spark_df = sc.read.format("com.databricks.spark.csv").option("header", "true").option("delimiter", ",").option(
            "inferSchema", "true").load(
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

        model_props = {
            self.wml_client.repository.ModelMetaNames.NAME: "{}".format(asset_name),
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
        published_model_details = self.wml_client.repository.store_model(model=model, meta_props=model_props,
                                                                         training_data=train_data, pipeline=pipeline)

        print("Published model details:\n{}".format(published_model_details))
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        print("Deploying model: {}, deployment name: {}".format(asset_name, deployment_name))
        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name,
                                                        asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        print("Deployment details:\n{}".format(deployment_details))

    def test_09_subscribe(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.aios_model_uid = TestAIOpenScaleClient.subscription.uid

    def test_10_unsubscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(TestAIOpenScaleClient.aios_model_uid)

    def test_11_subscribe(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.aios_model_uid = TestAIOpenScaleClient.subscription.uid

    def test_12_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_13_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_14_unbind(self):
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
