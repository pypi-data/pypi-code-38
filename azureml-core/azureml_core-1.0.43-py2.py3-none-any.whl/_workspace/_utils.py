# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import time
import requests
import uuid

from azureml._base_sdk_common.user_agent import get_user_agent
from azureml._base_sdk_common import _ClientSessionId
from azureml._restclient.constants import CALL_FUNCTION
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token

from azureml.exceptions import ProjectSystemException, UserErrorException

from .arm_template_builder import (
    ArmTemplateBuilder,
    build_storage_account_resource,
    build_keyvault_account_resource,
    build_application_insights_resource,
    build_workspace_resource
)


CONTAINER_REGISTRY = "ContainerRegistry"
STORAGE = "StorageAccount"
KEY_VAULT = "KeyVault"
APP_INSIGHTS = "AppInsights"
# Another spelling of application insights, used in developer workspaces
APPLICATION_INSIGHTS = "ApplicationInsights"
WORKSPACE = "Workspace"


def get_application_insights_region(workspace_region):
    '''
    Application Insights is not available in all locations. This function handles such exceptions
    by providing an alternative region for Application Insights.
    Update according to https://azure.microsoft.com/en-us/global-infrastructure/services/?products=monitor
    '''
    return {
        # TODO: We should replace this map with fetching actual appinsight locations using ARM API
        # So that we would only need to main a list of exceptions, not a list where appinsight is present.
        "australiaeast": "australiaeast",
        "canadacentral": "canadacentral",
        "centraluseuap": "eastus",
        "eastus": "eastus",
        "eastus2": "eastus2",
        "eastus2euap": "eastus",
        "northeurope": "northeurope",
        "southcentralus": "southcentralus",
        "southeastasia": "southeastasia",
        "uksouth": "uksouth",
        "westcentralus": "westus2",
        "westeurope": "westeurope",
        "westus2": "westus2",
        "centralindia": "centralindia",
        "eastasia": "eastasia",
        "japaneast": "japaneast",
    }.get(workspace_region, "eastus")


def arm_deploy_template_new_resources(auth, resource_group_name,
                                      location, subscription_id,
                                      workspace_name,
                                      deployment_name=None,
                                      storage=None,
                                      keyVault=None,
                                      containerRegistry=None,
                                      appInsights=None,
                                      show_output=True):
    """
    Deploys ARM template to create a team account with along with all the underlying dependencies.
    :param auth: auth object.
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param str resource_group_name: The name of resource group
    :param str location: The name of location
    :param subscription_id:
    :type subscription_id: str
    :param str workspace_name:
    :param str deployment_name: The name of the deployment
    """
    from azure.mgmt.resource.resources.models import DeploymentProperties
    resources_being_deployed = {}
    master_template = ArmTemplateBuilder()
    workspace_dependencies = []
    vault_name = ''
    storage_name = ''
    insights_name = ''
    location = location.lower().replace(" ", "")
    try:
        from .workspace_location_resolver import get_workspace_dependent_resource_location
        dependent_resource_location = get_workspace_dependent_resource_location(location)
    except:
        dependent_resource_location = location

    if keyVault is None:
        # Vault name must only contain alphanumeric characters and dashes and cannot start with a number.
        # Vault name must be between 3-24 alphanumeric characters.
        # The name must begin with a letter, end with a letter or digit, and not contain consecutive hyphens.
        vault_name = get_name_for_dependent_resource(workspace_name, 'keyvault')
        token = auth._get_arm_token()
        tenantId = fetch_tenantid_from_aad_token(token)
        keyvault_account = build_keyvault_account_resource(vault_name, dependent_resource_location, tenantId)
        master_template.add_resource(keyvault_account)
        workspace_dependencies.append("[resourceId('{}/{}', '{}')]".format('Microsoft.KeyVault', 'vaults', vault_name))
        keyVault = get_arm_resourceId(subscription_id, resource_group_name, 'Microsoft.KeyVault/vaults', vault_name)
        resources_being_deployed[vault_name] = (KEY_VAULT, None)

    if storage is None:
        storage_name = get_name_for_dependent_resource(workspace_name, 'storage')

        master_template.add_resource(build_storage_account_resource(storage_name, dependent_resource_location))
        workspace_dependencies.append(
            "[resourceId('{}/{}', '{}')]".format('Microsoft.Storage', 'storageAccounts', storage_name))
        storage = get_arm_resourceId(
            subscription_id,
            resource_group_name,
            'Microsoft.Storage/storageAccounts',
            storage_name)
        resources_being_deployed[storage_name] = (STORAGE, None)

    if appInsights is None:
        # Application name only allows alphanumeric characters, periods, underscores,
        # hyphens and parenthesis and cannot end in a period
        insights_name = get_name_for_dependent_resource(workspace_name, 'insights')

        insights_location = get_application_insights_region(location)
        master_template.add_resource(build_application_insights_resource(insights_name, insights_location))
        workspace_dependencies.append(
            "[resourceId('{}/{}', '{}')]".format('microsoft.insights', 'components', insights_name))
        appInsights = get_arm_resourceId(
            subscription_id,
            resource_group_name,
            'microsoft.insights/components',
            insights_name)
        resources_being_deployed[insights_name] = (APP_INSIGHTS, None)

    workspace_resource = build_workspace_resource(
        workspace_name,
        location,
        keyVault,
        containerRegistry,
        storageAccount=storage,
        appInsights=appInsights)
    workspace_resource['dependsOn'] = workspace_dependencies
    master_template.add_resource(workspace_resource)

    resources_being_deployed[workspace_name] = (WORKSPACE, None)

    template = master_template.build()
    properties = DeploymentProperties(template=template, parameters={}, mode='incremental')

    deployments_client = auth._get_service_client(ResourceManagementClient, subscription_id).deployments
    deployment_operations_client = auth._get_service_client(ResourceManagementClient,
                                                            subscription_id).deployment_operations

    deployment_name, lro_poller = _arm_deploy_template(deployments_client, resource_group_name,
                                                       deployment_name, properties)

    if show_output:
        while not lro_poller.done():
            _check_deployment_status(deployment_operations_client, resource_group_name,
                                     deployment_name, resources_being_deployed)
            time.sleep(5)
        # check if an exception was caught and if so print it
        # Otherwise we don't get valuable error messages as feedback to users
        if lro_poller._exception is not None:
            print("Unable to create the workspace. \n {}".format(lro_poller._exception))
            return vault_name, storage_name, insights_name
        # one last check to make sure all print statements make it
        _check_deployment_status(deployment_operations_client, resource_group_name,
                                 deployment_name, resources_being_deployed)
    else:
        try:
            lro_poller.wait()
        except Exception:
            print("Unable to create the workspace. \n {}".format(lro_poller._exception))

    return vault_name, storage_name, insights_name


def get_name_for_dependent_resource(workspace_name, resource_type):
    alphabets_str = ""
    for char in workspace_name.lower():
        if char.isalpha() or char.isdigit():
            alphabets_str = alphabets_str + char
    rand_str = str(uuid.uuid4()).replace("-", "")
    resource_name = alphabets_str[:8] + resource_type[:8] + rand_str

    return resource_name[:24]


def delete_storage(auth, resource_group_name, storage_name, subscription_id):
    """Deletes storage account"""
    client = auth._get_service_client(StorageManagementClient, subscription_id)
    return client.storage_accounts.delete(resource_group_name, storage_name)


def delete_insights(auth, resource_group_name, insights_name, subscription_id):
    """Deletes application insights"""
    rg_scope = "subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}".format(
        subscriptionId=subscription_id, resourceGroupName=resource_group_name)
    app_insights_id = rg_scope + "/providers/microsoft.Insights/components/{name}".format(
        name=insights_name)
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + app_insights_id + "?api-version=2015-05-01"
    requests.delete(url, headers=header)


def delete_keyvault(auth, resource_group_name, vault_name, subscription_id):
    """Deletes key vault"""
    client = auth._get_service_client(KeyVaultManagementClient, subscription_id)
    return client.vaults.delete(resource_group_name, vault_name)


def delete_kv_armId(auth, kv_armid, throw_exception=False):
    """Deletes kv account"""
    try:
        _check_valid_arm_id(kv_armid)
        subcription_id, resource_group, resource_name \
            = _get_subscription_id_resource_group_resource_name_from_arm_id(kv_armid)
        return delete_keyvault(auth, resource_group, resource_name, subcription_id)
    except Exception:
        if throw_exception:
            raise


def get_keyvault(auth, subscription_id, resource_group_name, keyvault_name):
    client = auth._get_service_client(KeyVaultManagementClient, subscription_id)
    return client.vaults.get(resource_group_name, keyvault_name)


def delete_insights_armId(auth, insights_armid, throw_exception=False):
    """Deletes insights account"""
    try:
        _check_valid_arm_id(insights_armid)
        subcription_id, resource_group, resource_name \
            = _get_subscription_id_resource_group_resource_name_from_arm_id(insights_armid)
        return delete_insights(auth, resource_group, resource_name, subcription_id)
    except Exception:
        if throw_exception:
            raise


def get_insights(auth, subscription_id, resource_group_name, insights_name):
    """Deletes application insights"""
    rg_scope = "subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}".format(
        subscriptionId=subscription_id, resourceGroupName=resource_group_name)
    app_insights_id = rg_scope + "/providers/microsoft.Insights/components/{name}".format(
        name=insights_name)
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + app_insights_id + "?api-version=2015-05-01"
    return requests.get(url, headers=header)


def delete_storage_armId(auth, storage_armid, throw_exception=False):
    """Deletes storage account"""
    try:
        _check_valid_arm_id(storage_armid)
        subcription_id, resource_group, resource_name \
            = _get_subscription_id_resource_group_resource_name_from_arm_id(storage_armid)
        return delete_storage(auth, resource_group, resource_name, subcription_id)
    except Exception:
        if throw_exception:
            raise


def _get_subscription_id_resource_group_resource_name_from_arm_id(arm_id):
    parts = arm_id.split('/')
    sub_id = parts[2]
    rg_name = parts[4]
    resource_name = parts[-1]
    return sub_id, rg_name, resource_name


def get_storage_account(auth, subscription_id, resource_group_name, storage_name):
    """Get storage account"""
    client = auth._get_service_client(StorageManagementClient, subscription_id)
    return client.storage_accounts.get_properties(resource_group_name, storage_name)


def _check_valid_arm_id(resource_arm_id):
    parts = resource_arm_id.split('/')
    if len(parts) != 9:
        raise UserErrorException("Wrong format of the given arm id={}".format(resource_arm_id))


def get_arm_resourceId(subscription_id,
                       resource_group_name,
                       provider,
                       resource_name):

    return '/subscriptions/{}/resourceGroups/{}/providers/{}/{}'.format(
        subscription_id,
        resource_group_name,
        provider,
        resource_name)


def create_storage_account(auth, resource_group_name, workspace_name,
                           location, subscription_id):
    """
    Creates a storage account.
    :param auth: auth object.
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param resource_group_name:
    :param workspace_name:
    :param location:
    :param subscription_id:
    :return: Returns storage account id.
    :rtype: str
    """
    if 'eastus2euap' == location.replace(' ', '').lower():
        location = 'eastus2'
    body = {'location': location,
            'sku': {'name': 'Standard_LRS'},
            'kind': 'Storage',
            'properties':
                {"encryption":
                    {"keySource": "Microsoft.Storage",
                     "services": {
                         "blob": {
                             "enabled": 'true'
                         }
                     }
                     },
                 "supportsHttpsTrafficOnly": True
                 }
            }
    rg_scope = "subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}".format(
        subscriptionId=subscription_id, resourceGroupName=resource_group_name)

    storage_account_id = rg_scope + "/providers/microsoft.Storage/storageAccounts/{workspaceName}".format(
        workspaceName=workspace_name)
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + storage_account_id + "?api-version=2016-12-01"

    response = requests.put(url, headers=header, json=body)
    if response.status_code not in [200, 201, 202]:
        # This could mean name conflict or max quota or something else, print the error message
        raise ProjectSystemException("Failed to create the storage account "
                                     "resource_group_name={}, workspace_name={}, "
                                     "subscription_id={}.\n Response={}".format(resource_group_name, workspace_name,
                                                                                subscription_id, response.text))

    return storage_account_id


def get_storage_key(auth, storage_account_id, storage_api_version):
    """

    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param storage_account_id:
    :param storage_api_version:
    :return:
    """
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + storage_account_id + "/listkeys?api-version=" + storage_api_version
    polling_interval = 3 * 60  # 3 minutes
    start_time = time.time()
    response = None
    while True and (time.time() - start_time < polling_interval):
        time.sleep(0.5)
        response = requests.post(url, headers=header)
        if response.status_code in [200]:
            break
    if storage_api_version == '2016-12-01':
        keys = response.json()
        access_key = keys['keys'][0]['value']
    else:
        keys = response.json()
        access_key = keys['primaryKey']
    return access_key


def _arm_deploy_template(deployments_client,
                         resource_group_name,
                         deployment_name,
                         properties):
    """
    Deploys ARM template to create a container registry.
    :param obj deployments_client: ARM deployments service client
    :param str resource_group_name: The name of resource group
    :param str deployment_name: The name of the deployment
    :param DeploymentProperties properties: The properties of a deployment
    """
    if deployment_name is None:
        import random
        deployment_name = '{0}_{1}'.format('Microsoft.MachineLearningServices', random.randint(100, 99999))

    headers = {
        "User-Agent": get_user_agent(),
        "x-ms-client-session-id": _ClientSessionId,
        CALL_FUNCTION: _arm_deploy_template.__name__
    }
    # set the polling frequency to 2 secs so that AzurePoller polls
    # for status of our operation every two seconds rather than the default of 30 secs
    operation_config = {}
    operation_config['long_running_operation_timeout'] = 2
    return (deployment_name,
            deployments_client.create_or_update(resource_group_name, deployment_name,
                                                properties, custom_headers=headers,
                                                operation_config=operation_config))


def get_arm_resource_id(resource_group_name, provider, resource_name, subscription_id):

    return '/subscriptions/{}/resourceGroups/{}/providers/{}/{}'.format(
        subscription_id, resource_group_name, provider, resource_name)


def get_location_from_resource_group(auth, resource_group_name, subscription_id):
    """

    :param auth:
    :param resource_group_name:
    :param subscription_id:
    :type subscription_id: str
    :return:
    """
    group = auth._get_service_client(ResourceManagementClient,
                                     subscription_id).resource_groups.get(resource_group_name)
    return group.location


def _check_deployment_status(deployment_operations_client,
                             resource_group_name,
                             deployment_name,
                             resources_being_deployed):
    try:
        headers = {
            "User-Agent": get_user_agent(),
            "x-ms-client-session-id": _ClientSessionId,
            CALL_FUNCTION: _check_deployment_status.__name__
        }
        deployment_operations = deployment_operations_client.list(resource_group_name,
                                                                  deployment_name,
                                                                  custom_headers=headers)

        for deployment_operation in deployment_operations:
            properties = deployment_operation.properties
            provisioning_state = properties.provisioning_state
            target_resource = properties.target_resource

            if target_resource is None:
                continue

            resource_name = target_resource.resource_name

            resource_type, previous_state = resources_being_deployed[resource_name]

            # duration comes in format: "PT1M56.3454108S"
            try:
                duration_parts = properties.additional_properties.get("duration").replace(
                    "PT", "").replace("S", "").split("M")
                if len(duration_parts) > 1:
                    duration = (float(duration_parts[0]) * 60) + float(duration_parts[1])
                else:
                    duration = float(duration_parts[0])

                duration = round(duration, 2)
            except Exception:
                duration = ""
                pass

            if provisioning_state == "Failed" and previous_state != "Failed":
                resources_being_deployed[resource_name] = (resource_type, provisioning_state)
                print("Deployment of {0} with name {1} failed.".format(resource_type, resource_name))
            # First time we're seeing this so let the user know it's being deployed
            elif properties.provisioning_state == "Running" and previous_state is None:
                print("Deploying {0} with name {1}.".format(resource_type, resource_name))
                resources_being_deployed[resource_name] = (resource_type, provisioning_state)
            # If the provisioning has already succeeded but we hadn't seen it Running before
            # (really quick deployment - so probably never happening) let user know resource
            # is being deployed and then let user know it has been deployed
            elif properties.provisioning_state == "Succeeded" and previous_state is None:
                print("Deploying {0} with name {1}.".format(resource_type, resource_name))
                print("Deployed {0} with name {1}. Took {2} seconds.".format(resource_type, resource_name, duration))
                resources_being_deployed[resource_name] = (resource_type, provisioning_state)
            # Finally, deployment has succeeded and was previously running, so mark it as finished
            elif properties.provisioning_state == "Succeeded" and previous_state != "Succeeded":
                print("Deployed {0} with name {1}. Took {2} seconds.".format(resource_type, resource_name, duration))
                resources_being_deployed[resource_name] = (resource_type, provisioning_state)
    except Exception:  # if the call fails for whatever reason, the user doesn't get feedback
        pass
