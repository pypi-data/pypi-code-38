# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Module for AML constants
"""
import os


SUCCESS_RETURN_CODE = 0
USER_ERROR_RETURN_CODE = 1
SYSTEM_ERROR_RETURN_CODE = 2

AMBIGUOUS_RETURN_CODE = None

MMS_MODEL_MANAGEMENT_ACCOUNT_PROFILE = 'viennaModelManagementAccountProfile.json'

MMS_API_VERSION = '2017-09-01-preview'
MMS_MODEL_URL_ENDPOINT = '/models'
MMS_MANIFEST_URL_ENDPOINT = '/manifests'
MMS_IMAGE_URL_ENDPOINT = '/images'
MMS_SERVICE_URL_ENDPOINT = '/services'
MMS_SERVICE_LIST_KEYS_URL_ENDPOINT = MMS_SERVICE_URL_ENDPOINT + '/{}/keys'
MMS_SERVICE_REGEN_KEYS_URL_ENDPOINT = MMS_SERVICE_URL_ENDPOINT + '/{}/regenerateKeys'
MMS_OPERATION_URL_ENDPOINT = '/operations/{}'

MMS_SYNC_TIMEOUT_SECONDS = 20
MMS_ASYNC_OPERATION_POLLING_INTERVAL_SECONDS = 5
MMS_ASYNC_OPERATION_POLLING_MAX_TRIES = 5
MMS_PAGINATED_RESPONSE_MAX_TRIES = 5
MMS_IMAGE_CREATE_OPERATION_POLLING_MAX_TRIES = 120
MMS_SERVICE_CREATE_OPERATION_POLLING_MAX_TRIES = 120

DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
SERVICE_DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service', 'data')
SUPPORTED_RUNTIMES = {'spark-py': 'SparkPython', 'python': 'Python', 'python-slim': 'PythonSlim'}
NINJA_RUNTIMES = ['mrs']
CREATE_CMD_SAMPLE = "az ml service create realtime -f <webservice file> -n <service name> [--model-file <model1> [--model-file <model2>] ...] [-p requirements.txt] [-d <dependency> [-d <dependency>] ...] [-s <schema>] [-r {0}] [-l] [-z <replicas>] [--collect-model-data]".format("|".join(SUPPORTED_RUNTIMES.keys()))  # noqa: E501
SCORING_URI_FORMAT = "{0}/score"
SWAGGER_URI_FORMAT = "{0}/swagger.json"
HEALTH_URI_FORMAT = "{0}/"
LOCAL_HEALTH_CHECK_POLLING_MAX_TRIES = 60
LOCAL_HEALTH_CHECK_POLLING_INTERVAL_SECONDS = 5
DEFAULT_INPUT_DATA = "!! YOUR DATA HERE !!"

# config keys
CURRENT_COMPUTE_CONFIG_KEY = 'current_config'
COMPUTE_NAME_KEY = 'name'
COMPUTE_RG_KEY = 'rg'
COMPUTE_SUB_KEY = 'sub'
COMPUTE_FE_URL_KEY = 'fe_url'
MODE_KEY = 'mode'
LOCAL = 'local'
CLUSTER = 'cluster'

MLC_RESOURCE_ID_FMT = '/subscriptions/{}/resourcegroups/{}/providers/Microsoft.MachineLearningCompute/operationalizationClusters/{}'  # noqa: E501
MLC_API_VERSION = '2017-08-01-preview'

TABLE_OUTPUT_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
APP_INSIGHTS_URL = 'https://analytics.applicationinsights.io/subscriptions/{}/resourcegroups/{}/components/{}#/discover/home?apptype=Other%20(preview)'  # noqa: E501

DEFAULT_WORKSPACE_CONFIG_KEY = 'aml_workspace'
