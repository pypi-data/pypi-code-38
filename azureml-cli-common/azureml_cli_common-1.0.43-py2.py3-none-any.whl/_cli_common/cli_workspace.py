# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Utility to get the workspace in Azure CLI (az).
"""

try:
    # python 3
    from configparser import ConfigParser
except ImportError:
    # python 2
    from ConfigParser import ConfigParser
import os
from azureml._cli_common.constants import DEFAULT_WORKSPACE_CONFIG_KEY
from azureml._cli_common.ml_cli_error import MlCliError
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.workspace import Workspace
from azure.cli.core._profile import Profile


def get_workspace(workspace_name=None, resource_group=None, subscription_id=None):
    if not workspace_name or not resource_group:
        config = ConfigParser()
        config.read(os.path.expanduser(os.path.join('~', '.azure', 'config')))
        if not workspace_name:
            if config.has_section('defaults') and config.has_option('defaults', DEFAULT_WORKSPACE_CONFIG_KEY):
                workspace_name = config.get('defaults', DEFAULT_WORKSPACE_CONFIG_KEY)
            else:
                raise MlCliError('Error, default workspace not set and workspace name parameter not provided.\n'
                                 'Please run "az configure --defaults {}=<workspace name>" '
                                 'to set default workspace,\n or provide a value for the --workspace-name '
                                 'parameter.'.format(DEFAULT_WORKSPACE_CONFIG_KEY))
        if not resource_group:
            if config.has_section('defaults') and config.has_option('defaults', 'group'):
                resource_group = config.get('defaults', 'group')
            else:
                raise MlCliError('Error, default resource group not set.\n'
                                 'Please run "az configure --defaults group=<resource group name>" '
                                 'to set default resource group,\n or provide a value for the --resource-group '
                                 'parameter.')

    subscription_id = subscription_id or _az_get_active_subscription_id()

    return Workspace.get(name=workspace_name, auth=AzureCliAuthentication(),
                         subscription_id=subscription_id, resource_group=resource_group)


def _az_get_active_subscription_id():
    return Profile().get_subscription()['id']
