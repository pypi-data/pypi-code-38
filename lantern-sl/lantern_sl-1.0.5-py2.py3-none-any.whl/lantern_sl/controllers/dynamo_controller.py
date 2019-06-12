import os
import sys
import boto3
import logging
import time
from lantern_sl.utils.json import json_float_to_decimal
from lantern_sl.utils.request import http_response, http_error, res_failed
from boto3.dynamodb.conditions import Key, Attr

log = logging.getLogger(__name__)

class ExceptionInvalidDynamoControllerType(Exception):
    """ Dynamo Type Not defined, this is a programming error """
    pass


class ExceptionInvalidDynamoControllerNotFound(Exception):
    """ Object not found in DB (404 error) """
    pass

def get_dynamo_connection(region_name=None, endpoint_url=None, force_live=False, force_local=False):
    """ Return a boto3 Dynamo Connection, live or test if pytest is running cases
    
    Keyword Arguments:
        region_name {str} -- Region to be used for dynamo(default: {None})
        endpoint_url {str} -- endpoint to be used (default: {None})
        force_live {bool} -- Force Live Connection to Dynamo (default: {False})
        force_local {bool} -- Force Local Connection to Dynamo (Default: {False})
    
    Returns:
        [Dynamo Connection] -- Dynamo Connection to be used
    """
    params = {}
    if not force_local:
        if region_name:
            params["region_name"] = region_name
        if endpoint_url:
            params["endpoint_url"] = endpoint_url
    if not force_live:
        if force_local or "pytest" in sys.modules:
            params["endpoint_url"] = "http://localhost:8989"
            params["region_name"] = "us-west-2"
    return boto3.resource("dynamodb", **params)
    

class DynamoController(object):
    """ Generic Dynamo Access Controller
        - Error handling
        - response message/data normalization
    """

    TYPE_GET = "get"
    TYPE_CREATE = "create"
    TYPE_UPDATE = "update"
    TYPE_DELETE = "delete"
    TYPE_FILTER = "filter"

    ORDER_ASC = "asc"
    ORDER_DESC = "desc"

    def __init__(self, table_name, debug=False):
        """ Initialize Dynamo Controller"""
        if not table_name:
            raise Exception("table_name can not be empty")
        self.dynamodb = get_dynamo_connection()
        self.table = self.dynamodb.Table(table_name)
        self.debug = debug if debug else os.getenv("LOCAL_USER", False)

    def get(self, primary_keys):
        """ return a the first element corresponding to the filter_data param"""
        return self._execute_operation(type=self.TYPE_GET, primary_keys=primary_keys)

    def create(self, data):
        """ Creates a new instance in the DB."""
        return self._execute_operation(type=self.TYPE_CREATE, data=data)

    def update(self, primary_keys, data):
        """ Update an existing object in the database"""
        res_update = self._execute_operation(type=self.TYPE_GET, primary_keys=primary_keys)
        if res_failed(res_update):
            return res_update
        self._execute_operation(type=self.TYPE_UPDATE, primary_keys=primary_keys, data=data)
        return self._execute_operation(type=self.TYPE_GET, primary_keys=primary_keys)

    def delete(self, primary_keys):
        """ Deletes a set of objects, corresponding to filter_data"""
        res = self._execute_operation(type=self.TYPE_GET, primary_keys=primary_keys)
        res_del = self._execute_operation(type=self.TYPE_DELETE, primary_keys=primary_keys)
        if res_failed(res_del):
            return res_del
        return res


    def get_filter_fe(self, fe_dict):
        """ generate filter_expression based on fe_dict received in event """
        tot_fe = None
        operation = fe_dict.get('operation', None)
        conditions = fe_dict.get('conditions', None)
        if not operation:
            raise Exception("'operation' is required")
        if not conditions:
            raise Exception("'conditions' is required")
        if operation != 'and' and operation != 'or':
            raise Exception("operation should be 'and' or 'or")
        for f in conditions:
            new_fe = None
            f_type = f.get('type', None)
            param1 = f.get('param1', None)
            param2 = f.get('param2', None)
            param3 = f.get('param3', None)
            if not param1 or param2 is None:
                raise Exception("type: {} defined but param1 or param2 not".format(f_type))
            if f_type == 'eq':
                new_fe = Attr(param1).eq(param2)
            if f_type == 'ne':
                new_fe = (Attr(param1).not_exists() | Attr(param1).ne(param2))
            if f_type == 'lt':
                new_fe = Attr(param1).lt(param2)
            if f_type == 'lte':
                new_fe = Attr(param1).lte(param2)
            if f_type == 'gt':
                new_fe = Attr(param1).gt(param2)
            if f_type == 'gte':
                new_fe = Attr(param1).gte(param2)
            if f_type == 'begins_with':
                new_fe = Attr(param1).begins_with(param2)
            if f_type == 'between':
                if param3 is None:
                    raise Exception("param3 not defined")
                new_fe = Attr(param1).between(param2, param3)

            if new_fe:
                if not tot_fe:
                    tot_fe = new_fe
                else:
                    if operation == "and":
                        tot_fe = tot_fe & new_fe
                    elif operation == "or":
                        tot_fe = tot_fe | new_fe
        return tot_fe
    
    def get_condition_expression_fe(self, c_express):
        """ return condition expression if c_express has all valid keys """
        total_condition = None
        if 'conditions' in c_express and len(c_express):
            for condition in c_express['conditions']:
                op = condition.get('op', None)
                key = condition.get('key', None)
                value = condition.get('value', None)
                value2 = condition.get('value2', None)
                new_fe = None
                if not op or not key or value is None:
                    raise Exception("Empty value in get_condition_expression op: {}, key:{}, value: {}, value2: {}".format(op, key, value, value2))
                if op == 'eq':
                    new_fe = Key(key).eq(value)
                if op == 'ne':
                    new_fe = not Key(key).eq(value)
                if op == 'lt':
                    new_fe = Key(key).lt(value)
                if op == 'lte':
                    new_fe = Key(key).lte(value)
                if op == 'gt':
                    new_fe = Key(key).gt(value)
                if op == 'gte':
                    new_fe = Key(key).gte(value)
                if op == 'begins_with':
                    new_fe = Key(key).begins_with(value)
                if op == 'between':
                    if value2 is None:
                        raise Exception("value2 not defined in between, condition_expression")
                    new_fe = Key(key).between(value, value2)
                
                if new_fe:
                    if not total_condition:
                        total_condition = new_fe
                    else:
                        total_condition = total_condition & new_fe
        return total_condition






    def filter(self, key, value, order_by=None, limit=50, next=None, index=None, order_type=ORDER_DESC, filter_expression=None, invert_result=False, condition_expression=None):
        """ Return all orders related to this user
            Params:
                - filter_expression is of type: FilterExpression (boto3), Veryyy flexible
                - first_element: Boolean, if set to True it will return the first element in the query of 404
                - filter_app: Boolean, if set to True, request is requiered and filter_expression will be overrided to filter by app_id
                    - Exception: if no request is provided
                    - ValueError: is filter_expression has a value
        """
        if index:
            index_name = index
        elif key and order_by:
            index_name = "{}-{}-index".format(key, order_by)
        else:
            index_name = "{}-index".format(key)

        params = {
            "IndexName": index_name,
            "Limit":limit,
        }
        if next:
            params["ExclusiveStartKey"] = next


        # Adding conditione expression from parameter or adding default (key/value)
        if condition_expression and type(condition_expression) == dict:
            condition_expression = json_float_to_decimal(condition_expression)
            condition_expression = self.get_condition_expression_fe(condition_expression)
            if condition_expression:
                params["KeyConditionExpression"] = Key(key).eq(value) & condition_expression
        if "KeyConditionExpression" not in params:
            params["KeyConditionExpression"] = Key(key).eq(value)


        #if request:
        #    time_filter,order = self._get_request_parameters(request)
        #    filter_expression = filter_expression & time_filter if time_filter and filterExpression else filter_expression

        if filter_expression and type(filter_expression) == dict:
            filter_expression = json_float_to_decimal(filter_expression)
            filter_expression = self.get_filter_fe(filter_expression)


        if filter_expression:
            params["FilterExpression"] = filter_expression

        #order_type = order if order else order_type
        if order_type == self.ORDER_DESC:
            params["ScanIndexForward"] = False
        
        # pulling data from DB
        data, count, next = self._execute_operation(type=self.TYPE_FILTER, primary_keys=params)
        # pulling data until next=None or len(data) >= limit
        while next and len(data) < limit:
            params["ExclusiveStartKey"] = next
            _data, _count, _next = self._execute_operation(type=self.TYPE_FILTER, primary_keys=params)
            data = data + _data
            count = count + _count
            next = _next
        if invert_result:
            data = list(reversed(data))

        return data, count, next

    '''
    def _get_request_parameters(self,request):
        """ Get order, initial timestamp and final timestamp from request
        """
        order               = request.args.get("order", None)
        initial_timestamp   = request.args.get("initial_timestamp", None)
        final_timestamp     = request.args.get("final_timestamp", None)

        if not final_timestamp and initial_timestamp:
            filter_expression   = Key('timestamp').gt(int(initial_timestamp))

        if not initial_timestamp and final_timestamp:
            filter_expression   = Key('timestamp').lt(int(final_timestamp))

        if not initial_timestamp and not final_timestamp:
            filter_expression   = None

        if initial_timestamp and final_timestamp:
            filter_expression   = Key('timestamp').between(int(initial_timestamp), int(final_timestamp))

        return filter_expression,order
    '''
    
    def _execute_operation(self, type, primary_keys=None, data=None):
        """ Execute the dynamo operation and return a proper response (success or error)"""
        try:
            if type == self.TYPE_GET:
                d_res = self.table.get_item(Key=primary_keys)
                if "Item" in d_res:
                    data = d_res["Item"]
                else:
                    raise ExceptionInvalidDynamoControllerNotFound("Not Found")
                return data
            elif type == self.TYPE_CREATE:
                data = json_float_to_decimal(data)
                d_res = self.table.put_item(Item=data)
                return data
            elif type == self.TYPE_UPDATE:
                data = json_float_to_decimal(data)
                d_res = self.table.update_item(
                    Key=primary_keys,
                    UpdateExpression="set " + ", ".join(["#{} = :_{}".format(key,key) for key in data.keys()]),
                    ExpressionAttributeNames={ "#{}".format(key):key for key in data.keys() },
                    ExpressionAttributeValues={ ":_{}".format(key): data[key] for key in data.keys() },
                    ReturnValues="UPDATED_NEW")
                return data
            elif type == self.TYPE_DELETE:
                d_res = self.table.delete_item(Key=primary_keys)
                return primary_keys
            elif type == self.TYPE_FILTER:
                response = self.table.query(**primary_keys)
                data = response["Items"] if response["Count"] != 0 else []
                code = response['ResponseMetadata']['HTTPStatusCode']
                count = response["Count"]
                next = response["LastEvaluatedKey"] if "LastEvaluatedKey" in response else None
                return data, count, next
            else:
                raise ExceptionInvalidDynamoControllerType("Type {} not defined in DynamoController".format(type))
        except ExceptionInvalidDynamoControllerType as e:
            raise e
        except ExceptionInvalidDynamoControllerNotFound as e:
            raise e
        except Exception as e:
            raise e
