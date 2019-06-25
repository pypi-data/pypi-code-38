# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._flighting.flight_cache import FlightCache

PROJECT_SERVICE_FC_NAME = "LocalProjectSystem"
SNAPSHOT_SERVICE_FC_NAME = "LocalRunSnapshot"
AML_CLI_SUBSCRIPTION_ID = "AML_CLI_SUBSCRIPTION_ID"


def get_snapshot_system_config_value(project_context=None):
    """Returns configuration value for the flight"""

    account_scope = project_context.get_workspace_uri_path()
    flight_cache = FlightCache()

    ''' Use a pre defined account id for snapshot tests and whitelist this account
    in flighting so that tests can use this id while the feature is still flighted'''
    precreated_workspaceid = '/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/' + \
        'resourceGroups/amlprojectsnapshottestsrg/providers/' + \
        'Microsoft.MachineLearningServices/workspaces/amlsnapshottestswsp'
    if (precreated_workspaceid in account_scope):
        return True
    if account_scope is not None:
        subscription_id = account_scope.split("subscriptions/", 1)[1].split("/resourceGroups", 1)[0]
    else:
        return False

    configuration_value = flight_cache.get_configuration_value(SNAPSHOT_SERVICE_FC_NAME,
                                                               subscription_id,
                                                               project_context.get_auth(),
                                                               account_scope)

    return configuration_value or False
