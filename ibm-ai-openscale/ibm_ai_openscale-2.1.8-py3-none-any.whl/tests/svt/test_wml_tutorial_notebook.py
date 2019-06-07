# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import wget
import os

from assertions import *
from preparation_and_cleaning import *

from ibm_ai_openscale import APIClient, APIClient4ICP

from ibm_ai_openscale import APIClient
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.utils import *
from ibm_ai_openscale.supporting_classes import PayloadRecord, Feature
from ibm_ai_openscale.supporting_classes.enums import *


@unittest.skipIf("ICP" in get_env(), "skipped on ICP")
class TestAIOpenScaleClient(unittest.TestCase):

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

    def test_run_notebook(self):
        #   Model building and deployment
        #   Load the training data from github

        if os.path.exists("german_credit_data_biased_training.csv"):
            os.remove("german_credit_data_biased_training.csv")
        wget.download(url="https://raw.githubusercontent.com/emartensibm/german-credit/master/german_credit_data_biased_training.csv")

        WML_CREDENTIALS = get_wml_credentials()
        DB_CREDENTIALS = get_database_credentials()

        KEEP_MY_INTERNAL_POSTGRES = False

        from pyspark.sql import SparkSession
        import pandas as pd
        import json

        spark = SparkSession.builder.getOrCreate()
        pd_data = pd.read_csv("german_credit_data_biased_training.csv", sep=",", header=0)
        df_data = spark.read.csv(path="german_credit_data_biased_training.csv", sep=",", header=True, inferSchema=True)
        df_data.head()

        #   Explore data    #
        df_data.printSchema()
        print("Number of records: " + str(df_data.count()))

        #   Create a model  #
        spark_df = df_data
        (train_data, test_data) = spark_df.randomSplit([0.8, 0.2], 24)

        MODEL_NAME = "Spark German Risk Model - Final"
        DEPLOYMENT_NAME = "Spark German Risk Deployment - Final"

        print("Number of records for training: " + str(train_data.count()))
        print("Number of records for evaluation: " + str(test_data.count()))

        spark_df.printSchema()

        from pyspark.ml.feature import OneHotEncoder, StringIndexer, IndexToString, VectorAssembler
        from pyspark.ml.evaluation import BinaryClassificationEvaluator
        from pyspark.ml import Pipeline, Model

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
                       "EmploymentDuration_IX", "Sex_IX",
                       "OthersOnLoan_IX", "OwnsProperty_IX", "InstallmentPlans_IX", "Housing_IX", "Job_IX",
                       "Telephone_IX", "ForeignWorker_IX",
                       "LoanDuration", "LoanAmount", "InstallmentPercent", "CurrentResidenceDuration", "LoanDuration",
                       "Age", "ExistingCreditsCount",
                       "Dependents"], outputCol="features")

        from pyspark.ml.classification import RandomForestClassifier
        classifier = RandomForestClassifier(featuresCol="features")

        pipeline = Pipeline(
            stages=[si_CheckingStatus, si_CreditHistory, si_EmploymentDuration, si_ExistingSavings, si_ForeignWorker,
                    si_Housing, si_InstallmentPlans, si_Job, si_LoanPurpose, si_OthersOnLoan,
                    si_OwnsProperty, si_Sex, si_Telephone, si_Label, va_features, classifier, label_converter])
        model = pipeline.fit(train_data)

        predictions = model.transform(test_data)
        evaluatorDT = BinaryClassificationEvaluator(rawPredictionCol="prediction")
        area_under_curve = evaluatorDT.evaluate(predictions)

        # default evaluation is areaUnderROC
        print("areaUnderROC = %g" % area_under_curve)

        #   Publish the model   #
        from watson_machine_learning_client import WatsonMachineLearningAPIClient
        import json

        wml_client = WatsonMachineLearningAPIClient(WML_CREDENTIALS)

        #   Remove existing model and deployment    #
        model_deployment_ids = wml_client.deployments.get_uids()
        for deployment_id in model_deployment_ids:
            deployment = wml_client.deployments.get_details(deployment_id)
            model_id = deployment['entity']['deployable_asset']['guid']
            if deployment['entity']['name'] == DEPLOYMENT_NAME:
                print('Deleting deployment id', deployment_id)
                wml_client.deployments.delete(deployment_id)
                print('Deleting model id', model_id)
                wml_client.repository.delete(model_id)
        wml_client.repository.list_models()

        model_props = {
            wml_client.repository.ModelMetaNames.NAME: "{}".format(MODEL_NAME),
            wml_client.repository.ModelMetaNames.EVALUATION_METHOD: "binary",
            wml_client.repository.ModelMetaNames.EVALUATION_METRICS: [
                {
                    "name": "areaUnderROC",
                    "value": area_under_curve,
                    "threshold": 0.7
                }
            ]
        }

        wml_models = wml_client.repository.get_details()
        model_uid = None
        for model_in in wml_models['models']['resources']:
            if MODEL_NAME == model_in['entity']['name']:
                model_uid = model_in['metadata']['guid']
                break

        if model_uid is None:
            print("Storing model ...")

            published_model_details = wml_client.repository.store_model(model=model, meta_props=model_props,
                                                                        training_data=train_data, pipeline=pipeline)
            model_uid = wml_client.repository.get_model_uid(published_model_details)
            print("Done")

        print(model_uid)

        #   Deploy the model    #
        wml_deployments = wml_client.deployments.get_details()
        deployment_uid = None
        for deployment in wml_deployments['resources']:
            if DEPLOYMENT_NAME == deployment['entity']['name']:
                deployment_uid = deployment['metadata']['guid']
                break

        if deployment_uid is None:
            print("Deploying model...")

            deployment = wml_client.deployments.create(artifact_uid=model_uid, name=DEPLOYMENT_NAME, asynchronous=False)
            deployment_uid = wml_client.deployments.get_uid(deployment)

        print("Model id: {}".format(model_uid))
        print("Deployment id: {}".format(deployment_uid))

        #   Configure OpenScale     #
        #   Cloud API KEY can be taken from functional id only   #


        #   Get Watson OpenScale GUID   #
        # import requests
        #
        # AIOS_GUID = None
        # token_data = {
        #     'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        #     'response_type': 'cloud_iam',
        #     'apikey': CLOUD_API_KEY
        # }
        #
        # response = requests.post('https://iam.bluemix.net/identity/token', data=token_data)
        # iam_token = response.json()['access_token']
        # iam_headers = {
        #     'Content-Type': 'application/json',
        #     'Authorization': 'Bearer %s' % iam_token
        # }
        #
        # resources = json.loads(
        #     requests.get('https://resource-controller.cloud.ibm.com/v2/resource_instances', headers=iam_headers).text)[
        #     'resources']
        # for resource in resources:
        #     if "aiopenscale" in resource['id'].lower():
        #         AIOS_GUID = resource['guid']
        #
        # AIOS_CREDENTIALS = {
        #     "instance_guid": AIOS_GUID,
        #     "apikey": CLOUD_API_KEY,
        #     "url": "https://api.aiopenscale.cloud.ibm.com"
        # }

        AIOS_CREDENTIALS = get_aios_credentials()
        AIOS_GUID = AIOS_CREDENTIALS['data_mart_id']

        if AIOS_GUID is None:
            print('Watson OpenScale GUID NOT FOUND')
        else:
            print(AIOS_GUID)

        ai_client = APIClient(aios_credentials=AIOS_CREDENTIALS)
        print(ai_client.version)

        try:
            data_mart_details = ai_client.data_mart.get_details()
            if 'internal_database' in data_mart_details and data_mart_details['internal_database']:
                if KEEP_MY_INTERNAL_POSTGRES:
                    print('Using existing internal datamart.')
                else:
                    if DB_CREDENTIALS is None:
                        print('No postgres credentials supplied. Using existing internal datamart')
                    else:
                        print('Switching to external datamart')
                        ai_client.data_mart.delete(force=True)
                        ai_client.data_mart.setup(db_credentials=DB_CREDENTIALS)
            else:
                print('Using existing external datamart')
        except:
            if DB_CREDENTIALS is None:
                print('Setting up internal datamart')
                ai_client.data_mart.setup(internal_db=True)
            else:
                print('Setting up external datamart')
                try:
                    ai_client.data_mart.setup(db_credentials=DB_CREDENTIALS)
                except:
                    print('Setup failed, trying Db2 setup')
                    ai_client.data_mart.setup(db_credentials=DB_CREDENTIALS, schema=DB_CREDENTIALS['username'])

        data_mart_details = ai_client.data_mart.get_details()
        print(data_mart_details)

        binding_uid = ai_client.data_mart.bindings.add('WML instance', WatsonMachineLearningInstance(WML_CREDENTIALS))
        if binding_uid is None:
            binding_uid = ai_client.data_mart.bindings.get_details()['service_bindings'][0]['metadata']['guid']
        bindings_details = ai_client.data_mart.bindings.get_details()
        ai_client.data_mart.bindings.list()

        print(binding_uid)

        ai_client.data_mart.bindings.list_assets()

        #   Subscriptions                               #
        #   Remove existing credit risk subscriptions   #

        subscriptions_uids = ai_client.data_mart.subscriptions.get_uids()
        for subscription in subscriptions_uids:
            sub_name = ai_client.data_mart.subscriptions.get_details(subscription)['entity']['asset']['name']
            if sub_name == MODEL_NAME:
                ai_client.data_mart.subscriptions.delete(subscription)
                print('Deleted existing subscription for', MODEL_NAME)

        subscription = ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(
            model_uid,
            problem_type=ProblemType.BINARY_CLASSIFICATION,
            input_data_type=InputDataType.STRUCTURED,
            label_column='Risk',
            prediction_column='predictedLabel',
            probability_column='probability',
            feature_columns=["CheckingStatus", "LoanDuration", "CreditHistory", "LoanPurpose", "LoanAmount",
                             "ExistingSavings", "EmploymentDuration", "InstallmentPercent", "Sex", "OthersOnLoan",
                             "CurrentResidenceDuration", "OwnsProperty", "Age", "InstallmentPlans", "Housing",
                             "ExistingCreditsCount", "Job", "Dependents", "Telephone", "ForeignWorker"],
            categorical_columns=["CheckingStatus", "CreditHistory", "LoanPurpose", "ExistingSavings",
                                 "EmploymentDuration", "Sex", "OthersOnLoan", "OwnsProperty", "InstallmentPlans",
                                 "Housing", "Job", "Telephone", "ForeignWorker"]
        ))

        if subscription is None:
            print('Subscription already exists; get the existing one')
            subscriptions_uids = ai_client.data_mart.subscriptions.get_uids()
            for sub in subscriptions_uids:
                if ai_client.data_mart.subscriptions.get_details(sub)['entity']['asset']['name'] == MODEL_NAME:
                    subscription = ai_client.data_mart.subscriptions.get(sub)

        subscriptions_uids = ai_client.data_mart.subscriptions.get_uids()
        ai_client.data_mart.subscriptions.list()

        subscription_details = subscription.get_details()

        #   Score the model so we can configure monitors    #
        credit_risk_scoring_endpoint = None
        print(deployment_uid)

        for deployment in wml_client.deployments.get_details()['resources']:
            if deployment_uid in deployment['metadata']['guid']:
                credit_risk_scoring_endpoint = deployment['entity']['scoring_url']

        print(credit_risk_scoring_endpoint)

        fields = ["CheckingStatus", "LoanDuration", "CreditHistory", "LoanPurpose", "LoanAmount", "ExistingSavings",
                  "EmploymentDuration", "InstallmentPercent", "Sex", "OthersOnLoan", "CurrentResidenceDuration",
                  "OwnsProperty", "Age", "InstallmentPlans", "Housing", "ExistingCreditsCount", "Job", "Dependents",
                  "Telephone", "ForeignWorker"]
        values = [
            ["no_checking", 13, "credits_paid_to_date", "car_new", 1343, "100_to_500", "1_to_4", 2, "female", "none", 3,
             "savings_insurance", 46, "none", "own", 2, "skilled", 1, "none", "yes"],
            ["no_checking", 24, "prior_payments_delayed", "furniture", 4567, "500_to_1000", "1_to_4", 4, "male", "none",
             4, "savings_insurance", 36, "none", "free", 2, "management_self-employed", 1, "none", "yes"],
            ["0_to_200", 26, "all_credits_paid_back", "car_new", 863, "less_100", "less_1", 2, "female", "co-applicant",
             2, "real_estate", 38, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["0_to_200", 14, "no_credits", "car_new", 2368, "less_100", "1_to_4", 3, "female", "none", 3, "real_estate",
             29, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["0_to_200", 4, "no_credits", "car_new", 250, "less_100", "unemployed", 2, "female", "none", 3,
             "real_estate", 23, "none", "rent", 1, "management_self-employed", 1, "none", "yes"],
            ["no_checking", 17, "credits_paid_to_date", "car_new", 832, "100_to_500", "1_to_4", 2, "male", "none", 2,
             "real_estate", 42, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["no_checking", 33, "outstanding_credit", "appliances", 5696, "unknown", "greater_7", 4, "male",
             "co-applicant", 4, "unknown", 54, "none", "free", 2, "skilled", 1, "yes", "yes"],
            ["0_to_200", 13, "prior_payments_delayed", "retraining", 1375, "100_to_500", "4_to_7", 3, "male", "none", 3,
             "real_estate", 37, "none", "own", 2, "management_self-employed", 1, "none", "yes"]
        ]

        payload_scoring = {"fields": fields, "values": values}
        scoring_response = wml_client.deployments.score(credit_risk_scoring_endpoint, payload_scoring)

        print('Single record scoring result:', '\n fields:', scoring_response['fields'], '\n values: ',
              scoring_response['values'][0])

        #   Quality monitoring and feedback logging     #
        #   Enable quality monitoring                   #
        time.sleep(10)
        subscription.quality_monitoring.enable(threshold=0.7, min_records=50)

        if os.path.exists("additional_feedback_data.json"):
            os.remove("additional_feedback_data.json")
        wget.download(url="https://raw.githubusercontent.com/emartensibm/german-credit/master/additional_feedback_data.json")

        with open('additional_feedback_data.json') as feedback_file:
            additional_feedback_data = json.load(feedback_file)
        subscription.feedback_logging.store(additional_feedback_data['data'])

        subscription.feedback_logging.show_table()

        run_details = subscription.quality_monitoring.run(background_mode=False)

        subscription.quality_monitoring.show_table()

        ai_client.data_mart.get_deployment_metrics()

        #   Fairness monitoring and explanations    #
        subscription.fairness_monitoring.enable(
            features=[
                Feature("Sex", majority=['male'], minority=['female'], threshold=0.95),
                Feature("Age", majority=[[26, 75]], minority=[[18, 25]], threshold=0.95)
            ],
            favourable_classes=['No Risk'],
            unfavourable_classes=['Risk'],
            min_records=200,
            training_data=pd_data
        )

        #   Score the model again now that monitoring is configured     #
        if os.path.exists("german_credit_feed.json"):
            os.remove("german_credit_feed.json")
        wget.download(url="https://raw.githubusercontent.com/emartensibm/german-credit/master/german_credit_feed.json")

        import random

        with open('german_credit_feed.json', 'r') as scoring_file:
            scoring_data = json.load(scoring_file)

        fields = scoring_data['fields']
        values = []
        for _ in range(200):
            values.append(random.choice(scoring_data['values']))
        payload_scoring = {"fields": fields, "values": values}

        scoring_response = wml_client.deployments.score(credit_risk_scoring_endpoint, payload_scoring)

        #   Run fairness monitor    #
        run_details = subscription.fairness_monitoring.run(background_mode=False)

        time.sleep(5)

        subscription.fairness_monitoring.show_table()

        #   Configure Explainability    #
        subscription.explainability.enable(training_data=pd_data)

        explainability_details = subscription.explainability.get_details()

        #   Run explanation for sample record   #
        transaction_id = subscription.payload_logging.get_table_content(limit=1)['scoring_id'].values[0]

        print(transaction_id)
        explain_run = subscription.explainability.run(transaction_id=transaction_id, background_mode=False)

        explain_result = pd.DataFrame.from_dict(explain_run['entity']['predictions'][0]['explanation_features'])
        explain_result.plot.barh(x='feature_name', y='weight', color='g', alpha=0.8);

        #   Custom monitors and metrics     #
        #   Register custom monitor     #
        def get_definition(monitor_name):
            monitors_definitions = ai_client.data_mart.monitors.get_details()['monitor_definitions']

            for definition in monitors_definitions:
                if monitor_name == definition['entity']['name']:
                    return definition

            return None

        from ibm_ai_openscale.supporting_classes import Metric, Tag

        monitor_name = 'my model performance'
        metrics = [Metric(name='sensitivity', lower_limit_default=0.8),
                   Metric(name='specificity', lower_limit_default=0.75)]
        tags = [Tag(name='region', description='customer geographical region')]

        existing_definition = get_definition(monitor_name)

        if existing_definition is None:
            my_monitor = ai_client.data_mart.monitors.add(name=monitor_name, metrics=metrics, tags=tags)
        else:
            my_monitor = existing_definition

        #   List monitors                   #
        #   Get monitors uids and details   #
        monitor_uid = my_monitor['metadata']['guid']

        print(monitor_uid)

        my_monitor = ai_client.data_mart.monitors.get_details(monitor_uid=monitor_uid)
        print('monitor definition details', my_monitor)

        #   Enable custom monitor for subscription      #
        from ibm_ai_openscale.supporting_classes import Threshold

        thresholds = [Threshold(metric_uid='sensitivity', lower_limit=0.9)]
        subscription.monitoring.enable(monitor_uid=monitor_uid, thresholds=thresholds)

        #   Get monitor configuration details   #
        subscription.monitoring.get_details(monitor_uid=monitor_uid)

        #   Storing custom metrics      #
        metrics = {"specificity": 0.78, "sensitivity": 0.67, "region": "us-south"}

        subscription.monitoring.store_metrics(monitor_uid=monitor_uid, metrics=metrics)

        #   List and get custom metrics     #
        subscription.monitoring.show_table(monitor_uid=monitor_uid)

        custom_metrics = subscription.monitoring.get_metrics(monitor_uid=monitor_uid, deployment_uid='credit')
        print(custom_metrics)

        custom_metrics_pandas = subscription.monitoring.get_table_content(monitor_uid=monitor_uid)

        #   Payload analytics                       #
        #   Run data distributions calculation      #

        from datetime import datetime

        start_date = "2018-01-01T00:00:00.00Z"
        end_date = datetime.utcnow().isoformat() + "Z"

        sex_distribution = subscription.payload_logging.data_distribution.run(
            start_date=start_date,
            end_date=end_date,
            group=['predictedLabel', 'Sex'],
            agg=['count'])

        #   Get data distributions as pandas dataframe      #
        sex_distribution_run_uid = sex_distribution['id']
        distributions_pd = subscription.payload_logging.data_distribution.get_run_result(
            run_id=sex_distribution_run_uid, format='pandas')
        print(distributions_pd)

        # subscription.payload_logging.data_distribution.show_chart(sex_distribution_run_uid)

        credit_history_distribution = subscription.payload_logging.data_distribution.run(
            start_date=start_date,
            end_date=end_date,
            group=['predictedLabel', 'CreditHistory'],
            agg=['count'])

        credit_history_distribution_run_uid = credit_history_distribution['id']

        # subscription.payload_logging.data_distribution.show_chart(credit_history_distribution_run_uid)


if __name__ == '__main__':
    unittest.main()
