import decimal
import os
import time
from time import sleep

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from properly_util_python.dynamo_helper import DynamoHelperBase, EnvironmentControlledDynamoHelper
from properly_util_python.helper_utils import dynamo_to_dict, dict_to_dynamo


def save_to_dynamo(table_name, item: dict, dynamodb_helper: DynamoHelperBase = EnvironmentControlledDynamoHelper(),
                   *args, **kwargs):
    item = add_dynamo_metadata(item)
    item['id'] = str(item['id'])
    if 'namespace' in kwargs:
        item['id'] = kwargs['namespace'] + '-' + item['id']

    table = dynamodb_helper.get_dynamo_db().Table(table_name)
    response = table.get_item(
        TableName=table_name,
        Key={
            'id': item['id']
        }
    )
    if not response.get('Item') or kwargs.get('overwrite_existing'):

        if response.get('Item'):
            print('overwrite existing dynamo table: %s id: %s' % (table_name, item['id']))

        response = table.put_item(Item=dict_to_dynamo(item))

        print('Saved to dynamo table: %s id: %s' % (table_name, item['id']))
    else:
        print('Skipping, this item already exists in dynamo table: %s id: %s' % (table_name, item['id']))

    return response



def add_dynamo_metadata(data):
    data['dynamoUploadTimeStamp'] = int(round(time.time() * 1000))

    return data


def get_dynamo_items(table_name, table_filter=None,
                     dynamodb_helper: DynamoHelperBase = EnvironmentControlledDynamoHelper(), *args, **kwargs):
    if not table_filter:
        table_filter = {}
    RETRY_EXCEPTIONS = ('ProvisionedThroughputExceededException',
                        'ThrottlingException')
    table = dynamodb_helper.get_dynamo_db().Table(table_name)

    get_table_items = table.scan
    if kwargs.get('table_get_type') == 'query':
        get_table_items = table.query

    response = get_table_items(**table_filter)
    items = response['Items']

    # todo watch for memory overflow in batching all the items as once
    # https://gist.github.com/shentonfreude/8d26ca1fc93fdb801b2c
    # https://github.com/boto/boto3/issues/597#issuecomment-323982159
    retries = 0
    max_retry = 3
    while 'LastEvaluatedKey' in response and retries < max_retry:
        if 'Limit' in table_filter and len(items) >= table_filter.get('Limit'):
            break
        try:

            print('items retrieved:', len(items))

            # if len(items) > 1000:
            #     return dynamo_to_dict(items)
            response = get_table_items(ExclusiveStartKey=response['LastEvaluatedKey'], **table_filter)
            items.extend(response['Items'])
            retries = 0
        except ClientError as err:
            if err.response['Error']['Code'] not in RETRY_EXCEPTIONS:
                raise
            print('WHOA, too fast, slow it down retries={}, items={}'.format(retries, len(items)), )
            sleep(1.3 ** retries)
            retries += 1  # TODO max limit

    return dynamo_to_dict(items)


def get_dynamo_item(table_name, item_value, item_key='id',
                    dynamodb_helper: DynamoHelperBase = EnvironmentControlledDynamoHelper(), ):
    """
    Return the dict representation of an object from dynamo
    :param table_name:
    :param item_value:
    :param item_key:
    :return: item: dict
    """
    deal_table = dynamodb_helper.get_dynamo_db().Table(table_name)
    resp = deal_table.get_item(
        TableName=table_name,
        Key={
            item_key: item_value
        }
    )
    item = resp.get('Item')

    if not item:
        return item

    return dynamo_to_dict(item)


def query_table(table_name, filter_key=None, filter_value=None, filter_type='eq'):
    """
    Perform a query operation on the table. Can specify filter_key (col name) and its value to be filtered.
    Returns the response.
    """

    # todo replace filter if-statements with, getattr filter statement

    if filter_type == 'not_exists':
        table_filter = {
            'FilterExpression': Attr(filter_key).not_exists()
        }
    elif filter_type == 'lt':
        table_filter = {
            'FilterExpression': Attr(filter_key).lt(filter_value)
        }
    elif filter_type == 'contains':
        table_filter = {
            'FilterExpression': Attr(filter_key).contains(filter_value)
        }

    else:
        table_filter = {
            'FilterExpression': Attr(filter_key).eq(filter_value)
        }

    items = get_dynamo_items(table_name, table_filter)
    return items


def get_last_key(config_id, table_name, META_KEY_MAP,
                 dynamodb_helper: DynamoHelperBase = EnvironmentControlledDynamoHelper()):
    # remove "dev" constant when moving to environment variables
    meta_table = dynamodb_helper.get_dynamo_db().Table(table_name)

    response = meta_table.get_item(
        Key={
            META_KEY_MAP["META_ID"]: config_id,
        })
    config = response.get('Item', None)
    if config is None:
        return None

    last_evaluated_key = config.get(META_KEY_MAP["META_CONFIG_VAL"])

    return last_evaluated_key


def set_last_key(last_eval_config, table_name, val, META_KEY_MAP,
                 dynamodb_helper: DynamoHelperBase = EnvironmentControlledDynamoHelper()):
    # remove "dev" constant when moving to environment variables
    meta_table = dynamodb_helper.get_dynamo_db().Table(table_name)

    now_seconds_epoch_utc = int(time.time())

    config_object = last_eval_config.copy()
    config_object[META_KEY_MAP["META_CONFIG_VAL"]] = val
    config_object[META_KEY_MAP["TABLE_UPDATED_AT"]] = now_seconds_epoch_utc

    meta_table.put_item(Item=config_object)




# Update 2018 07 24 : TODO:
# As of 0.10.48 of properly-util-python there is a utility library for accessing this
# Craig is not updating the calling code below as it is not currently covered in tests, but,
# this is a reminder to Craig or any others that the the next meaningful change
# and test in this area should consider replacing the code below with:
#
# from properly_util_python.distributed_property import DistributedPropertyTuple
#
#  ...
# self.last_key_config = DistributedPropertyTuple(property_id="4oH5qF2QiU2M3_ZNygpVMQ",
#                                                         short_name="LAST_PROCESSED_HISTORICAL_RAW_FOR_CLEANING",
#                                                         long_description="Last evaluated key of the historical-raw table so that multiple cleaners can cooperate on different parts of the table",
#                                                         dynamo_helper=EnvironmentControlledDynamoHelper())
#
# ...
#
# last_evaluated = response.get('LastEvaluatedKey', None)
# self.last_key_config.set_property(last_evaluated)
#

#####
# Update 2018 07 27
#
# This code is duplicated around in a number of places and shouldn't be, for now just trying to remove other places.
#
# Additionally should review the encapsulating boundary (call api seems wide)
# Still not fully removed



#############
# Query for next set of items


def query_some_items(table_name, META_CONFIG, META_KEY_MAP, limit=20,
                     dynamodb_helper: DynamoHelperBase = EnvironmentControlledDynamoHelper()):
    PROPERLY_STAGE = os.environ.get('PROPERLY_STAGE', 'dev')
    meta_table_name = "{0}-{1}".format(PROPERLY_STAGE, META_KEY_MAP["META_TABLE"])

    last_evaluated = get_last_key(META_CONFIG[META_KEY_MAP["META_ID"]], meta_table_name, META_KEY_MAP)
    table = dynamodb_helper.get_dynamo_db().Table(table_name)

    # performance improved by querying for the reserved value, no retries, if throughput exceeded will pick up next time
    if last_evaluated:
        response = table.query(
            IndexName=META_CONFIG['keyName'] + '-index',
            KeyConditionExpression=Key(META_CONFIG['keyName']).eq(-1),
            Limit=limit,
            ExclusiveStartKey=last_evaluated,
        )
    else:
        response = table.query(
            IndexName=META_CONFIG['keyName'] + '-index',
            KeyConditionExpression=Key(META_CONFIG['keyName']).eq(-1),
            Limit=limit)

    last_evaluated = response.get('LastEvaluatedKey', None)
    set_last_key(META_CONFIG, meta_table_name, last_evaluated, META_KEY_MAP)

    items_to_clean = response.get('Items')
    items_to_clean = dynamo_to_dict(items_to_clean)

    return items_to_clean


def scan_some_items(table_name, META_CONFIG, META_KEY_MAP, limit=20,
                    dynamodb_helper: DynamoHelperBase = EnvironmentControlledDynamoHelper()):
    meta_table_name = "{0}-{1}".format("dev", META_KEY_MAP["META_TABLE"])

    last_evaluated = get_last_key(META_CONFIG[META_KEY_MAP["META_ID"]], meta_table_name, META_KEY_MAP)
    table = dynamodb_helper.get_dynamo_db().Table(table_name)

    # scan should almost never be used, if you are calling this know the performance behavior
    # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-query-scan.html
    if last_evaluated:
        response = table.scan(
            Limit=limit,
            ExclusiveStartKey=last_evaluated,
        )
    else:
        response = table.scan(
            Limit=limit)

    last_evaluated = response.get('LastEvaluatedKey', None)
    set_last_key(META_CONFIG, meta_table_name, last_evaluated, META_KEY_MAP)

    items_to_clean = response.get('Items')
    items_to_clean = dynamo_to_dict(items_to_clean)

    return items_to_clean


def delete_dynamo_item(table_name, item_id, id_key='id', table_filter=None,
                       dynamodb_helper: DynamoHelperBase = EnvironmentControlledDynamoHelper(), *args, **kwargs):
    item = None
    if kwargs.get('return_deleted'):
        item = get_dynamo_item(table_name, item_id)

    table = dynamodb_helper.get_dynamo_db().Table(table_name)

    if table_filter:
        table.delete_item(**table_filter)
    else:
        table.delete_item(
            Key={
                id_key: item_id,
            }
        )

    print('deleting key:', item_id)
    return item
