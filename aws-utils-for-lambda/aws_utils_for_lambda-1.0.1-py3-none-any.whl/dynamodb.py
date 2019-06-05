import boto3
from aws_utils.response import ResponseObject


def get_item(table_name, key, region, output_format=None, raise_exception=False):
    data = None
    exception = None
    full_response = None
    session = boto3.session.Session()
    dynamodb = session.resource("dynamodb", region_name=region)
    try:
        full_response = dynamodb.meta.client.get_item(TableName=table_name, Key=key)
        data = full_response.get('Item')  # if no item, key exists but has no attribute
    except Exception as e:
        print(e)
        exception = e
    finally:
        if raise_exception:
            raise exception
        return ResponseObject(data=data,
                              exception=exception,
                              output_format=output_format,
                              full_response=full_response).response()


def put_item(table_name, item, region, output_format=None, raise_exception=False):
    data = None
    exception = None
    full_response = None
    session = boto3.session.Session()
    dynamodb = session.resource("dynamodb", region_name=region)
    try:
        full_response = dynamodb.meta.client.put_item(TableName=table_name, Item=item)
    except Exception as e:
        print(e)
        exception = e
    finally:
        if raise_exception:
            raise exception
        return ResponseObject(data=data,
                              exception=exception,
                              output_format=output_format,
                              full_response=full_response).response()
