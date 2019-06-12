from typing import Dict

import pymongo as pymongo
from retrying import retry

from sidecar.azure_clp.azure_clients import AzureClientsManager
from sidecar.azure_clp.data_store_service import DataStoreService
from sidecar.azure_clp.retrying_helpers import retry_if_connection_error


class AzureCosmosService(DataStoreService):
    default_db_name = "colony-sandboxes"
    default_sandboxes_collection_name = "sandboxes"
    uri_template = "mongodb://{account_name}:{master_key}@{account_name}.documents.azure.com:10255/?" \
                   "ssl=true&replicaSet=globaldb"

    def __init__(self, clients_manager: AzureClientsManager):
        super().__init__()
        self.cosmos_db_client = clients_manager.cosmos_db_client
        self.db_resource_group_name = clients_manager.management_resource_group
        self.account_name = "{}-sandbox-db".format(self.db_resource_group_name)

        # get the access key to the db
        my_keys = self._get_access_keys()
        self.master_key = my_keys.primary_master_key

        # python mongodb api tutorial: http://api.mongodb.com/python/current/tutorial.html
        uri = self.uri_template.format(account_name=self.account_name, master_key=self.master_key)
        self.client = pymongo.MongoClient(uri)

    @retry(stop_max_attempt_number=10, wait_fixed=1000, retry_on_exception=retry_if_connection_error)
    def _get_access_keys(self, ):
        my_keys = self.cosmos_db_client.database_accounts.list_keys(
            resource_group_name=self.db_resource_group_name,
            account_name=self.account_name)
        return my_keys

    def _get_collection(self, collection, db):
        return self.client[db][collection]

    def find_data_by_id(self, data_id: str) -> dict:
        return self._get_collection(collection=self.default_sandboxes_collection_name,
                                    db=self.default_db_name).find_one({'_id': data_id})

    def update_data(self, data_id: str, data, column_name: str):
        collection = self._get_collection(self.default_sandboxes_collection_name, self.default_db_name)
        collection.update_one(filter={'_id': data_id},
                              update={'$set': {column_name: data}})
