import os
import sys

os.environ['SPARK_HOME'] = "/opt/spark-2.0.2"
sys.path.append("/opt/spark-2.0.2/python")

import unittest
from client import WatsonMachineLearningAPIClient



class ServiceInstance(unittest.TestCase):

    def setUp(self):
        print("Service Instance: setting up credentials")
        self.wml_credentials = {
          "url": "https://ibm-watson-ml.mybluemix.net",
          "access_key": "WgyqOoemHVQ/lTxtrQAwKsYkycBPclIY01B8+FltGVikyVtt5h6wUccyhPR97tgtpxSFKe9cZoFYLlzgPf++qpWZYcc+6fawL9S0V+2V79Adc+zik+ZHJYrsBRl9GAcs",
          "username": "9ec7dc5e-359a-447c-a63e-8449d36b9642",
          "password": "27773259-3808-4809-ba06-58b646cd27a1",
          "instance_id": "360c510b-012c-4793-ae3f-063410081c3e"
        }

        self.client = WatsonMachineLearningAPIClient(self.wml_credentials)

    def test_create_client(self):
        print("creating client")
        self.assertEqual(type(self.client), WatsonMachineLearningAPIClient)


class Repository(unittest.TestCase):

    def setUp(self):
        print("Repository: setting up the client.")

        self.wml_credentials = {
          "url": "https://ibm-watson-ml.mybluemix.net",
          "access_key": "WgyqOoemHVQ/lTxtrQAwKsYkycBPclIY01B8+FltGVikyVtt5h6wUccyhPR97tgtpxSFKe9cZoFYLlzgPf++qpWZYcc+6fawL9S0V+2V79Adc+zik+ZHJYrsBRl9GAcs",
          "username": "9ec7dc5e-359a-447c-a63e-8449d36b9642",
          "password": "27773259-3808-4809-ba06-58b646cd27a1",
          "instance_id": "360c510b-012c-4793-ae3f-063410081c3e"
        }

        self.client = WatsonMachineLearningAPIClient(self.wml_credentials)
        self.guid_to_delete = None



    def tearDown(self):
        print("Repository: tearing down.")


    def test_1_get_models(self):
        print("1. Getting details...")
        models = self.client.repository.get_details()
        self.assertIsNotNone(models)

    """
    def test_2_get_models_invalid_guid(self):
        models = self.client.repository.get_details('1')
        self.assertIsNone(models)"""

    def test_3_publish_model(self):
        print("3. publishing model...")
        import wget
        import os

        link_to_data = 'https://apsportal.ibm.com/exchange-api/v1/entries/8044492073eb964f46597b4be06ff5ea/data?accessKey=9561295fa407698694b1e254d0099600'
        filename = wget.download(link_to_data)

        from pyspark import SparkConf, SparkContext
        from pyspark.sql import SparkSession

        conf = SparkConf().setAppName("wmlclient").setMaster("local")
        sc = SparkContext(conf=conf)
        spark = SparkSession.builder.getOrCreate()

        df_data = spark.read \
            .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
            .option('header', 'true') \
            .option('inferSchema', 'true') \
            .load(filename)

        os.remove(filename)

        splitted_data = df_data.randomSplit([0.8, 0.18, 0.02], 24)
        train_data = splitted_data[0]

        model_artifact = self.client.repository.load("3c9104a4-7f6e-4777-acec-3cec66911990")

        saved_model = self.client.repository.store_model(model=model_artifact, name="Unittest Model", training_data=train_data)

        self.client.guid_to_delete = saved_model.uid

        sc.stop()

        self.assertEqual(model_artifact, saved_model.model_instance())


    def test_4_load_model(self):
        print("4. loading model...")
        from pyspark.ml.pipeline import PipelineModel
        from pyspark import SparkConf, SparkContext
        from pyspark.sql import SparkSession

        conf = SparkConf().setAppName("wmlclient").setMaster("local")
        sc = SparkContext(conf=conf)
        spark = SparkSession.builder.getOrCreate()
        model_artifact = self.client.repository.load("3c9104a4-7f6e-4777-acec-3cec66911990")
        sc.stop()
        self.assertEqual(type(model_artifact), PipelineModel)


    def test_5_load_model_invalid_guid(self):
        print("5. Loading a model with invalid guid.")
        try:
            response = self.client.repository.load("3c9104")
        except Exception as e:
            print("Status: ", e.status)
            print("Reason: ", e.reason)
            print("Body: ", e.body)
            print("Headers: ", e.headers)
            self.assertEqual(e.status, 404)

    def test_6_delete_model(self):
        print("6. Deleting a model with valid guid.")
        try:
            deleted = self.client.repository.delete(self.client.guid_to_delete)
            self.assertEqual(deleted, None)
        except Exception as e:
            print(e)



    def test_7_delete_model_invalid_guid(self):
        print("7. Deleting a model with invalid guid.")
        try:
            response = self.client.repository.delete("3c9104")
        except Exception as e:
            print("Status: ", e.status)
            print("Reason: ", e.reason)
            print("Body: ", e.body)
            print("Headers: ", e.headers)
            self.assertEqual(e.status, 404)


class Deployments(unittest.TestCase):
    def setUp(self):
        print("Deployments: setting up credentials")

        self.wml_credentials = {
            "url": "https://ibm-watson-ml-svt.stage1.mybluemix.net",
            "access_key": "NB+hBdadW2C1pkyebTpU+YSkQxhC80sr9hI1Dyhl5euUJWkiDbuUFipBghr90P/KnR2Urnp4ZfzouMWYqPMVR/nmJBaSgi+xeMY8Wia68PB227SsqjgA5nvrX+eU9Sbr",
            "username": "0b5adb28-0eb0-44d7-95cb-9dc415f40bd9",
            "password": "69032c40-13c6-409a-8b81-2bc5e1ae1247",
            "instance_id": "ff558a0e-af34-40e9-9f13-2d51b1a4c8bb"
        }

        self.client = WatsonMachineLearningAPIClient(self.wml_credentials)
        self.model_guid = None
        self.deployment_url = None
        self.scoring_url = None
        # TODO get published model guid
        pass

    def test_get_deployments(self):
        self.assertIsNot(self.client.deployments.get_details())

    def test_get_deployment_invalid_url(self):
        self.assertIsNone(self.client.deployments.get_details('1'))

    def test_get_deployment(self):
        # TODO
        pass

    def test_create_deployment(self):
        # TODO
        self.assertIsNotNone(self.client.deployments.create(artifact_uid=self.model_guid))

    def test_delete_deployment(self):
        # TODO
        self.assertEqual(self.client.deployments.delete(deployment_url=self.deployment_url), '204')

    def test_delete_deployment_invalid_url(self):
        self.client.deployments.delete(deployment_url=self.deployment_url)

    def test_score_invalid(self):
        self.assertIsNone(self.client.deployments.score(scoring_url, {}))

    def test_score(self):
        # TODO
        payload = {}
        self.client.deployments.score(scoring_url, payload)
        pass

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
