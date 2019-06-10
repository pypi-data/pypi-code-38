# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""**AzureMLflowStore** provides a class to read and record run metrics and artifacts on Azure via MLflow."""

import logging
import os
import time

from mlflow.store.rest_store import RestStore
from mlflow.utils.rest_utils import MlflowHostCreds
from mlflow.exceptions import RestException

from azureml.core.authentication import AzureMLTokenAuthentication

from azureml._restclient.clientbase import DEFAULT_BACKOFF, DEFAULT_RETRIES
from azureml._restclient.run_client import RunClient

logger = logging.getLogger(__name__)

PARAM_PREFIX = "azureml.param."

_EXPERIMENT_NAME_ENV_VAR = "MLFLOW_EXPERIMENT_NAME"
_MLFLOW_RUN_ID_ENV_VAR = "MLFLOW_RUN_ID"


class AzureMLRestStore(RestStore):
    """Client for a remote tracking server accessed via REST API calls."""

    def __init__(self, service_context, artifact_uri=None):
        """Construct an AzureMLRestStore object."""
        logger.debug("Initializing the AzureMLRestStore")
        self._artifact_uri = artifact_uri
        self.service_context = service_context
        self.get_host_creds = self.get_host_credentials
        super(AzureMLRestStore, self).__init__(self.get_host_creds)

    def get_host_credentials(self):
        """Construct a MlflowHostCreds to be used for obtaining fresh credentials."""
        return MlflowHostCreds(
            self.service_context._get_run_history_url() +
            "/history/v1.0" + self.service_context._get_workspace_scope(),
            token=self.service_context.get_auth().get_authentication_header()["Authorization"][7:])

    def _call_endpoint(self, *args, **kwargs):
        total_retry = DEFAULT_RETRIES
        backoff = DEFAULT_BACKOFF
        for i in range(total_retry):
            try:
                return super(AzureMLRestStore, self)._call_endpoint(*args, **kwargs)
            except RestException as rest_exception:
                more_retries_left = i < total_retry - 1
                is_throttled = rest_exception.json.get("error", {"code": 0}).get("code") == "RequestThrottled"
                if more_retries_left and is_throttled:
                    logger.debug("There were too many requests. Try again soon.")
                    self._wait_for_retry(backoff, i, total_retry)
                else:
                    raise

    @classmethod
    def _wait_for_retry(cls, back_off, left_retry, total_retry):
        delay = back_off * 2 ** (total_retry - left_retry - 1)
        time.sleep(delay)

    def create_run(self, *args, **kwargs):
        """Create a run and set the AzureMLTokenAuthentication in the workspace."""
        auth = self.service_context.get_auth()
        logger.debug("Creating an Mlflow run with {} auth token".format(auth.__class__.__name__))
        run = super(AzureMLRestStore, self).create_run(*args, **kwargs)
        if not isinstance(auth, AzureMLTokenAuthentication) and _EXPERIMENT_NAME_ENV_VAR in os.environ:
            run_uuid = run.info.run_uuid
            experiment_name = os.environ[_EXPERIMENT_NAME_ENV_VAR]
            run_client = RunClient(self.service_context, experiment_name, run_uuid)
            token = run_client.get_token().token
            auth_object = AzureMLTokenAuthentication.create(
                azureml_access_token=token,
                expiry_time=None,
                host=self.service_context._get_run_history_url(),
                subscription_id=self.service_context.subscription_id,
                resource_group_name=self.service_context.resource_group_name,
                workspace_name=self.service_context.workspace_name,
                experiment_name=experiment_name,
                run_id=run_uuid
            )
            self.service_context._authentication = auth_object

        return run
