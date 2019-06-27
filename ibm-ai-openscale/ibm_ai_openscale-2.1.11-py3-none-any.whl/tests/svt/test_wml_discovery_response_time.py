# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import unittest
from preparation_and_cleaning import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.utils import requests_session


@unittest.skipIf("ICP" in get_env(), "Disabled on ICP...")
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

    test_uid = str(uuid.uuid4())

    wml_assets = []
    wml_assets_time = 0
    client_models = []
    client_models_time = 0
    restapi_models = []
    restapi_models_time = 0

    # in secs
    client_baseline = 10
    rest_api_baseline = 10
    correction = 0

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

        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=cls.database_credentials, schema=cls.schema)

        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = cls.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = cls.ai_client.data_mart.bindings.add("WML instance on Cloud", WatsonMachineLearningInstance(cls.wml_credentials))

        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(cls.binding_uid)

    def test_01_validate_client_response_time(self):
        start_time = time.time()
        asset_details = self.ai_client.data_mart.bindings.get_asset_details()
        duration = time.time() - start_time
        duration = int(duration)

        print("Baseline: {} secs, duration: {} secs".format(self.client_baseline + self.correction, duration))
        self.assertLess(duration, self.client_baseline + self.correction)

    def test_02_validate_rest_api_response_time(self):
        start_time = time.time()
        response = requests_session.get(
            self.ai_client._href_definitions.get_ml_gateway_discovery_href(binding_uid=self.binding_uid),
            headers=self.ai_client._get_headers())
        duration = time.time() - start_time
        duration = int(duration)
        print(response.json())

        print("Baseline: {} secs, duration: {} secs".format(self.rest_api_baseline + self.correction, duration))
        self.assertLess(duration, self.rest_api_baseline + self.correction)

    @classmethod
    def tearDownClass(cls):
        print("Deleting binding.")
        cls.ai_client.data_mart.bindings.delete(cls.binding_uid)

        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
