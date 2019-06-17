# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from collections import OrderedDict
import json


class ArmTemplateBuilder(object):

    def __init__(self):
        template = OrderedDict()
        template['$schema'] = \
            'https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#'
        template['contentVersion'] = '1.0.0.0'
        template['parameters'] = {}
        template['variables'] = {}
        template['resources'] = []
        self.template = template

    def add_resource(self, resource):
        self.template['resources'].append(resource)

    def build(self):
        return json.loads(json.dumps(self.template, default=set_default))


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def build_storage_account_resource(name, location):
    storage_account = {
        'type': 'Microsoft.Storage/storageAccounts',
        'name': name,
        'apiVersion': '2018-07-01',
        'location': location,
        'sku': {
            'name': 'Standard_LRS'
        },
        'kind': 'StorageV2',
        'dependsOn': [],
        'properties': {
            "encryption": {
                "services": {
                    "blob": {
                        "enabled": 'true'
                    },
                    "file": {
                        "enabled": 'true'
                    }
                },
                "keySource": "Microsoft.Storage"
            },
            "supportsHttpsTrafficOnly": True
        }
    }
    return storage_account


def build_application_insights_resource(name, location):
    application_insights = {
        'type': 'microsoft.insights/components',
        'name': name,
        'kind': 'web',
        'apiVersion': '2015-05-01',
        'location': location,
        'properties': {
            'Application_Type': 'web'
        }
    }
    return application_insights


def build_keyvault_account_resource(name, location, tenantId):
    keyvault_account = {
        'type': 'Microsoft.KeyVault/vaults',
        'name': name,
        'apiVersion': '2015-06-01',
        'location': location,
        'dependsOn': [],
        'properties': {
                'enabledForDeployment': 'true',
                'enabledForTemplateDeployment': 'true',
                'enabledForVolumeEncryption': 'true',
                'tenantId': tenantId,
                'accessPolicies': [],
                'sku': {
                    'name': 'Standard',
                    'family': 'A'
                }
        }
    }
    return keyvault_account


def build_workspace_resource(name, location, keyVault, containerRegistry, storageAccount,
                             appInsights):
    workspace_resource = {
        'type': 'Microsoft.MachineLearningServices/workspaces',
        'name': name,
        'apiVersion': '2018-11-19',
        'identity': {
                'type': 'systemAssigned'
        },
        'location': location,
        'resources': [],
        'dependsOn': [],
        'properties': {
            'containerRegistry': containerRegistry,
            'keyVault': keyVault,
            'applicationInsights': appInsights,
            'friendlyName': name,
            'storageAccount': storageAccount
        }
    }
    return workspace_resource
