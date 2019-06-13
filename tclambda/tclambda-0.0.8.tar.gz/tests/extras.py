import json
import os
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

import boto3

import tclambda

s3client = boto3.client("s3")

TC_THIS_BUCKET = os.getenv("TC_THIS_BUCKET")


class FunctionBuilder:
    def __init__(self, function, *args, **kwargs):
        key = f"tests/{function}/{datetime.utcnow():%Y/%m/%d/%H%M%S}/{uuid4()}.json"
        self.message_body = {
            "function": function,
            "args": args,
            "kwargs": kwargs,
            "result_store": key,
        }
        self.result = tclambda.function.LambdaResult(TC_THIS_BUCKET, key)

    @property
    def sqs(self):
        return {"Records": [{"body": json.dumps(self.message_body)}]}


class ProxyFunctionBuilder:
    def __init__(self, function, *args, **kwargs):
        key = f"{function}/{datetime.utcnow():%Y/%m/%d/%H%M%S}/{uuid4()}.json"
        result_store = f"tests/results/{key}"
        proxy_store = f"tests/proxy/{key}"
        self.message_body = {
            "function": function,
            "args": args,
            "kwargs": kwargs,
            "result_store": result_store,
        }
        self.proxy_body = {"proxy": proxy_store}
        s3client.put_object(
            Bucket=TC_THIS_BUCKET, Key=proxy_store, Body=json.dumps(self.message_body)
        )
        self.result = tclambda.function.LambdaResult(TC_THIS_BUCKET, result_store)

    @property
    def sqs(self):
        return {"Records": [{"body": json.dumps(self.proxy_body)}]}


@dataclass
class LambdaContext:
    function_name: str

    def get_remaining_time_in_millis(self):
        return 100000


def my_test_function():
    return "success"


async def my_async_test_function():
    return "async success"


def my_test_exception():
    raise ValueError("This is a value error")


def my_invalid_return_value():
    return datetime(2019, 5, 3)
