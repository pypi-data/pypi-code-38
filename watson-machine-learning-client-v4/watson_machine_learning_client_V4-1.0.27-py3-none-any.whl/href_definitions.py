################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

import re

TRAINING_MODEL_HREF_PATTERN = u'{}/v4/trainings/{}'
TRAINING_MODELS_HREF_PATTERN = u'{}/v4/trainings'
REPO_MODELS_FRAMEWORKS_HREF_PATTERN = u'{}/v3/models/frameworks'

INSTANCE_ENDPOINT_HREF_PATTERN = u'{}/v3/wml_instance'
INSTANCE_BY_ID_ENDPOINT_HREF_PATTERN = u'{}/v3/wml_instances/{}'
TOKEN_ENDPOINT_HREF_PATTERN = u'{}/v3/identity/token'
EXPERIMENTS_HREF_PATTERN = u'{}/v4/experiments'
EXPERIMENT_HREF_PATTERN = u'{}/v4/experiments/{}'
EXPERIMENT_RUNS_HREF_PATTERN = u'{}/v3/experiments/{}/runs'
EXPERIMENT_RUN_HREF_PATTERN = u'{}/v3/experiments/{}/runs/{}'

PUBLISHED_MODEL_HREF_PATTERN = u'{}/v4/models/{}'
PUBLISHED_MODELS_HREF_PATTERN = u'{}/v4/models'
LEARNING_CONFIGURATION_HREF_PATTERN = u'{}/v3/wml_instances/{}/published_models/{}/learning_configuration'
LEARNING_ITERATION_HREF_PATTERN = u'{}/v3/wml_instances/{}/published_models/{}/learning_iterations/{}'
LEARNING_ITERATIONS_HREF_PATTERN = u'{}/v3/wml_instances/{}/published_models/{}/learning_iterations'
EVALUATION_METRICS_HREF_PATTERN = u'{}/v3/wml_instances/{}/published_models/{}/evaluation_metrics'
FEEDBACK_HREF_PATTERN = u'{}/v3/wml_instances/{}/published_models/{}/feedback'

DEPLOYMENTS_HREF_PATTERN = u'{}/v4/deployments'
DEPLOYMENT_HREF_PATTERN = u'{}/v4/deployments/{}'
DEPLOYMENT_JOB_HREF_PATTERN = u'{}/v4/jobs'
DEPLOYMENT_JOBS_HREF_PATTERN = u'{}/v4/jobs/{}'
DEPLOYMENT_ENVS_HREF_PATTERN = u'{}/v4/deployments/environments'
DEPLOYMENT_ENV_HREF_PATTERN = u'{}/v4/deployments/environments/{}'

MODEL_LAST_VERSION_HREF_PATTERN = u'{}/v4/models/{}'
DEFINITION_HREF_PATTERN = u'{}/v3/ml_assets/training_definitions/{}'
DEFINITIONS_HREF_PATTERN = u'{}/v3/ml_assets/training_definitions'

FUNCTION_HREF_PATTERN = u'{}/v4/functions/{}'
FUNCTION_LATEST_CONTENT_HREF_PATTERN = u'{}/v4/functions/{}/content'
FUNCTIONS_HREF_PATTERN = u'{}/v4/functions'

RUNTIME_HREF_PATTERN = u'{}/v4/runtimes/{}'
RUNTIMES_HREF_PATTERN = u'{}/v4/runtimes'
CUSTOM_LIB_HREF_PATTERN = u'{}/v4/libraries/{}'
CUSTOM_LIBS_HREF_PATTERN = u'{}/v4/libraries'

IAM_TOKEN_API = u'{}&grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey'
IAM_TOKEN_URL = u'{}/oidc/token'
PROD_URL = ['https://us-south.ml.cloud.ibm.com','https://eu-gb.ml.cloud.ibm.com','https://eu-de.ml.cloud.ibm.com','https://jp-tok.ml.cloud.ibm.com','https://ibm-watson-ml.mybluemix.net','https://ibm-watson-ml.eu-gb.bluemix.net']

PIPELINES_HREF_PATTERN=u'{}/v4/pipelines'
PIPELINE_HREF_PATTERN=u'{}/v4/pipelines/{}'


SPACES_HREF_PATTERN = u'{}/v4/spaces'
SPACE_HREF_PATTERN = u'{}/v4/spaces/{}'
API_VERSION = u'/v4'
SPACES=u'/spaces'
PIPELINES=u'/pipelines'
EXPERIMENTS=u'/experiments'
LIBRARIES=u'/libraries'
RUNTIMES=u'/runtimes'
DEPLOYMENTS = u'/deployments'


def is_url(s):
    res = re.match('https?:\/\/.+', s)
    return res is not None


def is_uid(s):
    res = re.match('[a-z0-9\-]{36}', s)
    return res is not None


class HrefDefinitions:
    def __init__(self, wml_credentials):
        self._wml_credentials = wml_credentials

    def get_training_href(self, model_uid):
        return TRAINING_MODEL_HREF_PATTERN.format(self._wml_credentials['url'], model_uid)

    def get_trainings_href(self):
        return TRAINING_MODELS_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_repo_models_frameworks_href(self):
        return REPO_MODELS_FRAMEWORKS_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_instance_endpoint_href(self):
        return INSTANCE_ENDPOINT_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_instance_by_id_endpoint_href(self):
        return INSTANCE_BY_ID_ENDPOINT_HREF_PATTERN.format(self._wml_credentials['url'], self._wml_credentials['instance_id'])

    def get_token_endpoint_href(self):
        return TOKEN_ENDPOINT_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_published_model_href(self, model_uid):
        return PUBLISHED_MODEL_HREF_PATTERN.format(self._wml_credentials['url'], model_uid)

    def get_published_models_href(self):
        return PUBLISHED_MODELS_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_learning_configuration_href(self, model_uid):
        return LEARNING_CONFIGURATION_HREF_PATTERN.format(self._wml_credentials['url'], self._wml_credentials['instance_id'], model_uid)

    def get_learning_iterations_href(self, model_uid):
        return LEARNING_ITERATIONS_HREF_PATTERN.format(self._wml_credentials['url'], self._wml_credentials['instance_id'], model_uid)

    def get_learning_iteration_href(self, model_uid, iteration_uid):
        return LEARNING_ITERATION_HREF_PATTERN.format(self._wml_credentials['url'], self._wml_credentials['instance_id'], model_uid, iteration_uid)

    def get_evaluation_metrics_href(self, model_uid):
        return EVALUATION_METRICS_HREF_PATTERN.format(self._wml_credentials['url'], self._wml_credentials['instance_id'], model_uid)

    def get_feedback_href(self, model_uid):
        return FEEDBACK_HREF_PATTERN.format(self._wml_credentials['url'], self._wml_credentials['instance_id'], model_uid)

    def get_model_last_version_href(self, artifact_uid):
        return MODEL_LAST_VERSION_HREF_PATTERN.format(self._wml_credentials['url'], artifact_uid)

    def get_deployments_href(self):
        return DEPLOYMENTS_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_experiments_href(self):
        return EXPERIMENTS_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_experiment_href(self, experiment_uid):
        return EXPERIMENT_HREF_PATTERN.format(self._wml_credentials['url'], experiment_uid)

    def get_experiment_runs_href(self, experiment_uid):
        return EXPERIMENT_RUNS_HREF_PATTERN.format(self._wml_credentials['url'], experiment_uid)

    def get_experiment_run_href(self, experiment_uid, experiment_run_uid):
        return EXPERIMENT_RUN_HREF_PATTERN.format(self._wml_credentials['url'], experiment_uid, experiment_run_uid)

    def get_deployment_href(self, deployment_uid):
        return DEPLOYMENT_HREF_PATTERN.format(self._wml_credentials['url'], deployment_uid)

    def get_definition_href(self, definition_uid):
        return DEFINITION_HREF_PATTERN.format(self._wml_credentials['url'], definition_uid)

    def get_definitions_href(self):
        return DEFINITIONS_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_function_href(self, ai_function_uid):
        return FUNCTION_HREF_PATTERN.format(self._wml_credentials['url'], ai_function_uid)

    def get_function_latest_revision_content_href(self, ai_function_uid):
        return FUNCTION_LATEST_CONTENT_HREF_PATTERN.format(self._wml_credentials['url'], ai_function_uid)

    def get_functions_href(self):
        return FUNCTIONS_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_runtime_href_v4(self, runtime_uid):
        return u'/v4/runtimes/{}'.format(runtime_uid)

    def get_runtime_href(self, runtime_uid):
        return RUNTIME_HREF_PATTERN.format(self._wml_credentials['url'], runtime_uid)

    def get_runtimes_href(self):
        return RUNTIMES_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_custom_library_href(self, library_uid):
        return CUSTOM_LIB_HREF_PATTERN.format(self._wml_credentials['url'], library_uid)

    def get_custom_libraries_href(self):
        return CUSTOM_LIBS_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_pipeline_href(self, pipeline_uid):
        return PIPELINE_HREF_PATTERN.format(self._wml_credentials['url'], pipeline_uid)

    def get_pipelines_href(self):
        return PIPELINES_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_space_href(self, spaces_uid):
        return SPACE_HREF_PATTERN.format(self._wml_credentials['url'], spaces_uid)

    def get_spaces_href(self):
        return SPACES_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_async_deployment_job_href(self):
        return DEPLOYMENT_JOB_HREF_PATTERN.format(self._wml_credentials['url'])

    def get_async_deployment_jobs_href(self, job_uid):
        return DEPLOYMENT_JOBS_HREF_PATTERN.format(self._wml_credentials['url'],job_uid)


    def get_async_deployment_jobs_href(self, deployment_uid, job_uid):
        return DEPLOYMENT_JOBS_HREF_PATTERN.format(self._wml_credentials['url'], deployment_uid, job_uid)

    def get_iam_token_api(self):
        return IAM_TOKEN_API.format(self._wml_credentials['apikey'])

    def get_iam_token_url(self):
        if (self._wml_credentials['url'] in PROD_URL):
            return IAM_TOKEN_URL.format('https://iam.cloud.ibm.com')
        else:
            return IAM_TOKEN_URL.format('https://iam.test.cloud.ibm.com')

    # def get_envs_href(self):
    #     return DEPLOYMENT_ENVS_HREF_PATTERN.format(self._wml_credentials['url'])
    #
    # def get_env_href(self, env_id):
    #     return DEPLOYMENT_ENV_HREF_PATTERN.format(self._wml_credentials['url'],env_id)

