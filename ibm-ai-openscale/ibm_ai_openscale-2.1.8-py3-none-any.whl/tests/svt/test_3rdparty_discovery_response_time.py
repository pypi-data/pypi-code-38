# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import unittest
import time
import requests
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *


@unittest.skipIf("ICP" in get_env(), "Disabled on ICP...")
class TestAIOpenScaleClient(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    binding_uid = None
    scoring_url = None
    labels = None
    ai_client = None
    wml_client = None
    subscription = None
    test_uid = str(uuid.uuid4())
    source_uid = None
    transaction_id = None
    azure_get_webervices = []
    azure_get_webervices_time = 0
    client_get_webervices = []
    client_get_webervices_time = 0
    restapi_get_webervices = []
    restapi_get_webervices_time = 0

    sm_models = []
    sm_models_time = 0
    sm_deployments = []
    client_endpoints = []
    client_endpoints_time = 0
    restapi_endpoints = []
    restapi_endpoints_time = 0

    custom_deployments = []
    custom_models = []
    custom_deployments_time = 0
    client_deployments = []
    client_deployments_time = 0
    restapi_deployments = []
    restapi_deployments_time = 0

    # in secs
    sagemaker_client_baseline = 10
    sagemaker_rest_api_baseline = 10

    azure_client_baseline = 120
    azure_rest_api_baseline = 120

    custom_client_baseline = 5
    custom_rest_api_baseline = 5

    # Azure configuration
    azure_credentials = {
        "client_id": "29f007c5-4c45-4210-8a88-9a40136f0ddd",
        "client_secret": "e4d8b0fa-73f7-4b77-83a7-0b424d92940f",
        "subscription_id": "744bca72-2299-451c-b682-ed6fb75fb671",
        "tenant": "fcf67057-50c9-4ad4-98f3-ffca64add9e9"
    }

    # AWS configuration
    aws_credentials = {
        "access_key_id": "AKIAI3LQITG4RLLSUIHA",
        "secret_access_key": "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",
        "region": "us-east-1"
    }

    # Custom deployment configuration
    custom_credentials = {
        "url": "http://169.63.194.147:31520",
        "username": "xxx",
        "password": "yyy",
        "request_headers": {"content-type": "application/json"}
    }

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

        cls.ai_client.data_mart.setup(db_credentials=cls.database_credentials, schema=cls.schema)

    def test_01_azure_prepare_binding(self):
        TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("Azure ml engine", AzureMachineLearningInstance(self.azure_credentials))

    def test_02_azure_validate_client_response_time(self):
        start_time = time.time()
        asset_details = self.ai_client.data_mart.bindings.get_asset_details()
        duration = time.time() - start_time
        duration = int(duration)

        print(type(asset_details))
        print("Asset details: {}".format(asset_details))

        print("Baseline: {} secs, duration: {} secs".format(self.azure_client_baseline, duration))
        self.assertLess(duration, self.azure_client_baseline)
        self.assertIsNotNone(asset_details)

    def test_03_azure_validate_rest_api_response_time(self):
        start_time = time.time()

        url = self.ai_client._href_definitions.get_ml_gateway_discovery_href(binding_uid=self.binding_uid)
        headers = self.ai_client._get_headers()

        print("URL: {}".format(url))
        print("header: {}".format(headers))

        response = requests.get(url=url, headers=headers, verify=False)
        print(response)
        print(response.status_code)
        print(response.text)
        duration = time.time() - start_time
        duration = int(duration)

        print("Baseline: {} secs, duration: {} secs".format(self.azure_rest_api_baseline, duration))
        self.assertLess(duration, self.azure_rest_api_baseline)
        self.assertEqual(200, response.status_code)

    def test_04_sagemaker_prepare_binding(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)
        TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("SageMaker ml engine", SageMakerMachineLearningInstance(self.aws_credentials))

    def test_05_sagemaker_validate_client_response_time(self):
        start_time = time.time()
        asset_details = self.ai_client.data_mart.bindings.get_asset_details()
        duration = time.time() - start_time
        duration = int(duration)

        print("Baseline: {} secs, duration: {} secs".format(self.sagemaker_client_baseline, duration))
        self.assertLess(duration, self.sagemaker_client_baseline)
        self.assertIsNotNone(asset_details)

    def test_06_sagemaker_validate_rest_api_response_time(self):
        start_time = time.time()
        response = requests.get(
            self.ai_client._href_definitions.get_ml_gateway_discovery_href(binding_uid=self.binding_uid),
            headers=self.ai_client._get_headers())
        duration = time.time() - start_time
        duration = int(duration)

        print("Baseline: {} secs, duration: {} secs".format(self.sagemaker_rest_api_baseline, duration))
        self.assertLess(duration, self.sagemaker_rest_api_baseline)
        self.assertEqual(200, response.status_code)

    def test_07_custom_prepare_binding(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)
        TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("My Custom deployment", CustomMachineLearningInstance(self.custom_credentials))

    def test_08_custom_validate_client_response_time(self):
        start_time = time.time()
        asset_details = self.ai_client.data_mart.bindings.get_asset_details()

        duration = time.time() - start_time
        duration = int(duration)

        print("Baseline: {} secs, duration: {} secs".format(self.custom_client_baseline, duration))
        self.assertLess(duration, self.custom_client_baseline)
        self.assertIsNotNone(asset_details)

    def test_09_custom_validate_rest_api_response_time(self):
        start_time = time.time()
        response = requests.get(
            self.ai_client._href_definitions.get_ml_gateway_discovery_href(binding_uid=self.binding_uid),
            headers=self.ai_client._get_headers())
        duration = time.time() - start_time
        duration = int(duration)

        print("Baseline: {} secs, duration: {} secs".format(self.custom_rest_api_baseline, duration))
        self.assertLess(duration, self.custom_rest_api_baseline)
        self.assertEqual(200, response.status_code)

    @classmethod
    def tearDownClass(cls):
        print("Unbinding.")
        cls.ai_client.data_mart.bindings.delete(cls.binding_uid)

        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
