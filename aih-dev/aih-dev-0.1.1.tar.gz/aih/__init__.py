from .aih import AIH
import json


def init(app_id, secret_key):
    return AIH(app_id=app_id, secret_key=secret_key)


class LambdaException(Exception):
    pass


def response(data):
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": json.dumps(data),
        "headers": {
            'Access-Control-Allow-Origin': '*'
        },
    }
