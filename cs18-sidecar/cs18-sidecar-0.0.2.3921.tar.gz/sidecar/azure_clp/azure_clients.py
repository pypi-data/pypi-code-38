from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.cosmosdb import CosmosDB
from msrestazure.azure_active_directory import ServicePrincipalCredentials
from azure.mgmt.storage import StorageManagementClient
from azure.cosmosdb.table import TableService


class AzureCredentialsProvider:

    def __init__(self, management_resource_group: str, subscription_id: str, application_id: str,
                 application_secret: str, tenant_id: str):
        self.management_resource_group = management_resource_group
        self.subscription_id = subscription_id
        self.application_id = application_id
        self.application_key = application_secret
        self.tenant = tenant_id

    def get_service_principal(self):
        return ServicePrincipalCredentials(client_id=self.application_id,
                                           secret=self.application_key,
                                           tenant=self.tenant)


class AzureClientsManager:

    def __init__(self, credentials_provider: AzureCredentialsProvider):
        self._credentials_provider = credentials_provider
        self._service_principal = self._credentials_provider.get_service_principal()
        self._cosmos_client = None
        self._compute_client = None
        self._table_service = None
        self._storage_client = None

    @property
    def management_resource_group(self):
        return self._credentials_provider.management_resource_group

    @property
    def cosmos_db_client(self):
        if self._cosmos_client is None:
            self._cosmos_client = CosmosDB(self._service_principal, self._credentials_provider.subscription_id)
        return self._cosmos_client

    @property
    def compute_client(self):
        if self._compute_client is None:
            self._compute_client = ComputeManagementClient(self._service_principal,
                                                           self._credentials_provider.subscription_id)
        return self._compute_client

    @property
    def storage_client(self):
        if self._storage_client is None:
            self._storage_client = StorageManagementClient(self._service_principal,
                                                           self._credentials_provider.subscription_id)
        return self._storage_client

    @property
    def table_service(self):
        if self._table_service is None:
            self._table_service = TableService(account_name=self.management_resource_group.replace("-", ""),
                                               account_key=self._get_storage_key())

        return self._table_service

    def _get_storage_key(self):
        storage_keys = self.storage_client.storage_accounts.list_keys(self.management_resource_group,
                                                                      self.management_resource_group.replace("-", ""))
        storage_keys = {v.key_name: v.value for v in storage_keys.keys}
        return storage_keys['key1']
