# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure datalake datastore class."""
import azureml.data.constants as constants

from .abstract_datastore import AbstractDatastore


class AbstractADLSDatastore(AbstractDatastore):
    """Base ADLS Datastore class."""

    def __init__(self, workspace, name, datastore_type, tenant_id, client_id, client_secret, resource_url,
                 authority_url):
        """Initialize a new Azure Data Lake Datastore.

        :param workspace: the workspace this datastore belongs to
        :type workspace: str
        :param name: the datastore name
        :type name: str
        :param tenant_id: the Directory ID/Tenant ID of the service principal
        :type tenant_id: str
        :param client_id: the Client ID/Application ID of the service principal
        :type client_id: str
        :param client_secret: the secret of the service principal
        :type client_secret: str
        :param resource_url: the resource url, which determines what operations will be performed on
            the data lake store
        :type resource_url: str, optional
        """
        super(AbstractADLSDatastore, self).__init__(workspace, name, datastore_type)
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource_url = resource_url
        self.authority_url = authority_url

    def _as_dict(self, hide_secret=True):
        output = super(AbstractADLSDatastore, self)._as_dict()
        output["tenant_id"] = self.tenant_id
        output["client_id"] = self.client_id
        output["resource_url"] = self.resource_url
        output["authority_url"] = self.authority_url

        if not hide_secret:
            output["client_secret"] = self.client_secret

        return output


class AzureDataLakeDatastore(AbstractADLSDatastore):
    """Datastore backed by Azure Data Lake."""

    def __init__(self, workspace, name, store_name, tenant_id, client_id, client_secret,
                 resource_url=None, authority_url=None, subscription_id=None, resource_group=None):
        """Initialize a new Azure Data Lake Datastore.

        :param workspace: the workspace this datastore belongs to
        :type workspace: str
        :param name: the datastore name
        :type name: str
        :param store_name: the ADLS store name
        :type store_name: str
        :param tenant_id: the Directory ID/Tenant ID of the service principal
        :type tenant_id: str
        :param client_id: the Client ID/Application ID of the service principal
        :type client_id: str
        :param client_secret: the secret of the service principal
        :type client_secret: str
        :param resource_url: the resource url, which determines what operations will be performed on
            the data lake store
        :type resource_url: str, optional
        :param subscription_id: the ID of the subscription the ADLS store belongs to
        :type subscription_id: str, optional
        :param resource_group: the resource group the ADLS store belongs to
        :type resource_group: str, optional
        """
        super(AzureDataLakeDatastore, self).__init__(workspace, name, constants.AZURE_DATA_LAKE, tenant_id, client_id,
                                                     client_secret, resource_url, authority_url)
        self.store_name = store_name
        self.subscription_id = subscription_id
        self.resource_group = resource_group

    def _as_dict(self, hide_secret=True):
        output = super(AzureDataLakeDatastore, self)._as_dict(hide_secret)
        output["store_name"] = self.store_name
        output["subscription_id"] = self.subscription_id
        output["resource_group"] = self.resource_group
        return output


class AzureDataLakeGen2Datastore(AbstractADLSDatastore):
    """Datastore backed by Azure Data Lake Gen2."""

    def __init__(self, workspace, name, container_name, account_name, tenant_id, client_id, client_secret,
                 resource_url, authority_url, protocol, endpoint):
        """Initialize a new Azure Data Lake Gen2 Datastore.

        :param workspace: the workspace this datastore belongs to
        :type workspace: str
        :param name: the datastore name
        :type name: str
        :param container_name: The name of the azure blob container.
        :type container_name: str
        :param account_name: The storage account name.
        :type account_name: str
        :param tenant_id: the Directory ID/Tenant ID of the service principal
        :type tenant_id: str
        :param client_id: the Client ID/Application ID of the service principal
        :type client_id: str
        :param client_secret: the secret of the service principal
        :type client_secret: str
        :param resource_url: the resource url, which determines what operations will be performed on
        the data lake store
        :type resource_url: str, optional
        :param authority_url: the authority url used to authenticate the user
        :type authority_url: str, optional
        :param protocol: Protocol to use to connect to the blob container. If None, defaults to https.
        :type protocol: str, optional
        :param endpoint: The endpoint of the blob container. If None, defaults to core.windows.net.
        :type endpoint: str, optional
        """
        super(AzureDataLakeGen2Datastore, self).__init__(workspace, name, constants.AZURE_DATA_LAKE_GEN2, tenant_id,
                                                         client_id, client_secret, resource_url, authority_url)
        self.container_name = container_name
        self.account_name = account_name
        self.protocol = protocol
        self.endpoint = endpoint

    def _as_dict(self, hide_secret=True):
        output = super(AzureDataLakeGen2Datastore, self)._as_dict(hide_secret)
        output["container_name"] = self.container_name
        output["account_name"] = self.account_name
        output["protocol"] = self.protocol
        output["endpoint"] = self.endpoint
        return output
