import json
from typing import List

import jsonpickle
from azure.common import AzureMissingResourceHttpError
from azure.cosmosdb.table import Entity
from azure.cosmosdb.table.tableservice import TableService

from sidecar.azure_clp.data_store_service import DataStoreService


class AzureTableService(DataStoreService):

    def __init__(self, table_service: TableService,
                 default_table_name: str = "colonySandboxes",
                 default_partition_key: str = "colonySandbox"):
        super().__init__()
        self.default_partition_key = default_partition_key
        self.table_service = table_service
        self.default_table_name = default_table_name

    def create_table(self):
        # create the table if not exists
        if not self.table_service.exists(table_name=self.default_table_name):
            self.table_service.create_table(table_name=self.default_table_name,
                                            fail_on_exist=False)

    def insert_data(self, data: dict, data_id: str = None):
        entity = self._to_entity(data=data, data_id=data_id)
        self.table_service.insert_entity(table_name=self.default_table_name,
                                         entity=entity)

    def find_data_by_id(self, data_id: str) -> dict:
        entity = {}
        try:
            entity = self.table_service.get_entity(table_name=self.default_table_name,
                                                   row_key=data_id,
                                                   partition_key=self.default_partition_key)
        except AzureMissingResourceHttpError:
            return {}

        res = self._convert_entity_to_dict(entity)
        return res

    def find_data_by_ids(self, id_column_name: str, ids: List[str] = None) -> List[dict]:
        if not ids:
            return list()
        ids_filter = " or ".join([id_column_name.replace("-", "__") + " eq '{0}' ".format(str(iid)) for iid in ids])
        query_entities_gen = self.table_service.query_entities(table_name=self.default_table_name,
                                                               filter=ids_filter)

        return list([self._convert_entity_to_dict(entity) for entity in query_entities_gen])

    def delete_data_by_id(self, data_id: str) -> bool:
        entity = self.table_service.delete_entity(table_name=self.default_table_name,
                                                  partition_key=self.default_partition_key,
                                                  row_key=data_id)
        return entity is None

    def update_data(self, data_id: str, data: dict, column_name: str):
        entity = self._to_entity(data={column_name: data},
                                 data_id=data_id)

        self.table_service.merge_entity(table_name=self.default_table_name,
                                        entity=entity)

    def _to_entity(self, data: dict, data_id: str):
        task = Entity()
        task.PartitionKey = self.default_partition_key
        task.RowKey = str(data_id)
        for k, v in data.items():
            task[str(k).replace("-", "__")] = jsonpickle.encode(v)
        return task

    def _convert_entity_to_dict(self, entity):
        res = {}
        remove_keys = {'PartitionKey', "RowKey", "Timestamp", "etag"}
        for k, v in entity.items():
            key = str(str(k).replace("__", "-"))
            if key not in remove_keys:
                res[key] = jsonpickle.decode(v)
        return res
