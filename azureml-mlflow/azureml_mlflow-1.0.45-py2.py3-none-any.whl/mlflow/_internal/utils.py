# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""mlflow helper functions."""

import logging
import os
import re

from azureml.core.authentication import ArmTokenAuthentication, AzureMLTokenAuthentication
from azureml._restclient.service_context import ServiceContext

from mlflow.exceptions import MlflowException

from six.moves.urllib import parse

_IS_REMOTE = "is-remote"
_REGION = "region"
_SUB_ID = "sub-id"
_RES_GRP = "res-grp"
_WS_NAME = "ws-name"
_EXP_NAME = "experiment"
_RUN_ID = "runid"
_AUTH_HEAD = "auth"
_AUTH_TYPE = "auth-type"
_TRUE_QUERY_VALUE = "True"

_TOKEN_PREFIX = "Bearer "
_TOKEN_QUERY_NAME = "token"

logger = logging.getLogger(__name__)


def tracking_uri_decomp(path):
    """
    Parse the tracking URI into a dictionary.

    The tracking URI contains the scope information for the workspace.
    """
    regex = "(.*)" \
        "\\/subscriptions\\/(.+)" \
        "\\/resourceGroups\\/(.+)" \
        "\\/providers\\/Microsoft.MachineLearningServices" \
        "\\/workspaces\\/([^\\/]+)"

    pattern = re.compile(regex)
    mo = pattern.match(path)

    ret = {}
    ret[_SUB_ID] = mo.group(2)
    ret[_RES_GRP] = mo.group(3)
    ret[_WS_NAME] = mo.group(4)

    return ret


def artifact_uri_decomp(path):
    """
    Parse the artifact URI into a dictionary.

    The artifact URI contains the scope information for the workspace, the experiment and the run_id.
    """
    regex_old = "/(.+)" \
        "\\/runs\\/(.+)\\/artifacts"

    regex_new = "(.*)" \
        "\\/subscriptions\\/(.+)" \
        "\\/resourceGroups\\/(.+)" \
        "\\/providers\\/Microsoft.MachineLearningServices" \
        "\\/workspaces\\/(.+)" \
        "\\/experiments\\/(.+)" \
        "\\/runs\\/([^\\/]+)"

    ret = {}
    try:
        mo = re.compile(regex_new).match(path)
        ret[_SUB_ID] = mo.group(2)
        ret[_RES_GRP] = mo.group(3)
        ret[_WS_NAME] = mo.group(4)
        ret[_EXP_NAME] = mo.group(5)
        ret[_RUN_ID] = mo.group(6)
    except:
        mo = re.compile(regex_old).match(path)
        ret[_EXP_NAME] = mo.group(1)
        ret[_RUN_ID] = mo.group(2)

    return ret


def get_service_context_from_artifact_url(parsed_url):
    parsed_artifacts_path = artifact_uri_decomp(parsed_url.path)
    logger.debug("Creating service context from the artifact uri")
    subscription_id = parsed_artifacts_path[_SUB_ID]
    resource_group_name = parsed_artifacts_path[_RES_GRP]
    workspace_name = parsed_artifacts_path[_WS_NAME]
    queries = dict(parse.parse_qsl(parsed_url.query))
    if _TOKEN_QUERY_NAME not in queries:
        raise MlflowException("An authorization token was not set in the artifact uri")

    auth = AzureMLTokenAuthentication(
        queries[_TOKEN_QUERY_NAME],
        host=parsed_url.netloc,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name)

    return ServiceContext(subscription_id=subscription_id,
                          resource_group_name=resource_group_name,
                          workspace_name=workspace_name,
                          workspace_id=None,
                          authentication=auth)


def get_service_context_from_tracking_url(parsed_url):
    """Create a Service Context object out of a parsed URL."""
    logger.debug("Creating a Service Context object from the tracking uri")
    parsed_path = tracking_uri_decomp(parsed_url.path)
    subscription_id = parsed_path[_SUB_ID]
    resource_group_name = parsed_path[_RES_GRP]
    workspace_name = parsed_path[_WS_NAME]

    queries = dict(parse.parse_qsl(parsed_url.query))
    if _AUTH_HEAD not in queries:
        from mlflow.tracking.utils import _TRACKING_TOKEN_ENV_VAR
        token = os.environ.get(_TRACKING_TOKEN_ENV_VAR)
        if token is not None:
            logger.debug("The _TRACKING_TOKEN_ENV_VAR is set. Using ArmTokenAuthentication.")
            auth = ArmTokenAuthentication(token)
        else:
            logger.debug("The token is neither set in the env variable nor sent in the url."
                         "Using the default InteractiveLoginAuthentication.")
            auth = None
    else:
        if queries[_AUTH_TYPE] == AzureMLTokenAuthentication.__name__:
            logger.debug("Using AzureMLTokenAuthentication")
            auth = AzureMLTokenAuthentication(
                queries[_AUTH_HEAD],
                host=parsed_url.netloc,
                subscription_id=subscription_id,
                resource_group_name=resource_group_name,
                workspace_name=workspace_name,
            )
        else:
            logger.debug("Using ArmTokenAuthentication")
            auth = ArmTokenAuthentication(queries[_AUTH_HEAD])

    return ServiceContext(subscription_id=subscription_id,
                          resource_group_name=resource_group_name,
                          workspace_name=workspace_name,
                          workspace_id=None,
                          authentication=auth)
