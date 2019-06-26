

import time
from properly_util_python.dynamo_helper import DynamoHelperBase
from properly_util_python.table_helper import TableHelper


class DistributedPropertyTuple:
    META_ID = "id"
    META_DESCRIPTION = "description"
    META_SHORT_NAME = "shortName"
    META_CONFIG_VAL = 'configVal'

    TABLE_UPDATED_AT_MILLIS = 'updatedAtMillis'

    def __init__(self, property_id: str, short_name: str, long_description: str, dynamo_helper: DynamoHelperBase):
        self.dynamo_helper = dynamo_helper
        self.table_helper = TableHelper(dynamo_helper=dynamo_helper)
        self.property_id = property_id
        self.short_name = short_name
        self.long_description = long_description

    def set_property(self, property_val:dict):

        meta_table = self.table_helper.get_table(TableHelper.META_TABLE_NAME)
        now_millis_epoch_utc = int(1000*time.time())

        config_object = {
            DistributedPropertyTuple.META_ID: self.property_id,
            DistributedPropertyTuple.META_SHORT_NAME: self.short_name,
            DistributedPropertyTuple.META_DESCRIPTION: self.long_description,
            DistributedPropertyTuple.TABLE_UPDATED_AT_MILLIS: now_millis_epoch_utc,
            DistributedPropertyTuple.META_CONFIG_VAL: property_val
        }

        meta_table.put_item(Item=config_object)

    def get_property(self):
        meta_table = self.table_helper.get_table(TableHelper.META_TABLE_NAME)

        response = meta_table.get_item(
            Key={
                DistributedPropertyTuple.META_ID: self.property_id,
            })
        config = response.get('Item', None)
        if config is None:
            return None

        last_evaluated_key = config.get(DistributedPropertyTuple.META_CONFIG_VAL)

        return last_evaluated_key


