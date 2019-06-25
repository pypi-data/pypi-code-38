# https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
import asyncio
import json
import logging
import os
import traceback
from io import StringIO

import boto3

from .exceptions import RetryException
from .extras import sentry_init

sentry_init()
logging.basicConfig(level=logging.INFO)

s3client = boto3.client("s3")
cloudwatch = boto3.client("cloudwatch")

TC_THIS_BUCKET = os.getenv("TC_THIS_BUCKET")


class LambdaHandler:
    def __init__(self, json_encoder_class=json.JSONEncoder):
        self.logger = logging.getLogger("tclambda.LambdaHandler")
        self.functions = {"ping": lambda: "pong"}
        self.json_encoder_class = json_encoder_class

    def register(self, name=None):
        def wrapper(func):
            nonlocal name
            if name is None:
                name = func.__name__
            self.logger.debug(f"Registering function {func} with name {name}")
            self.functions[name] = func
            return func

        return wrapper

    def __call__(self, event, context):
        self.context = context
        self.logger.info(event)
        if "Records" in event:
            return asyncio.run(self.handle_sqs_event(event, context))
        elif "function" in event or "proxy" in event:
            return asyncio.run(self.handle_message(event, context))

    async def handle_sqs_event(self, event, context):
        handlers = []
        for record in event["Records"]:
            body = record["body"]
            try:
                message = json.loads(body)
            except json.JSONDecodeError:
                self.logger.exception(f'Couldn\'t decode body "{body}"')
            else:
                future = asyncio.ensure_future(self.handle_message(message, context))
                handlers.append(future)
        await asyncio.gather(*handlers)

    async def handle_message(self, message, context):
        if "proxy" in message:
            obj = s3client.get_object(Bucket=TC_THIS_BUCKET, Key=message["proxy"])
            message = json.load(obj["Body"])
        result_body = {}
        result_store = message.get("result_store")

        try:
            func_name = message.get("function")
            if not func_name:
                self.logger.error(f'Message does not contain key "function" {message}')
                raise TypeError(f'Message does not contain key "function" {message}')
            func = self.functions.get(func_name)
            if not func:
                available_functions = sorted(self.functions.keys())
                self.logger.error(
                    f"Function {func_name} is not a registered function in {available_functions}"
                )
                raise TypeError(f"Function {func_name} does not exist")

            args = message.get("args", ())
            kwargs = message.get("kwargs", {})

            if asyncio.iscoroutinefunction(func):
                result_body["result"] = await func(*args, **kwargs)
            else:
                result_body["result"] = func(*args, **kwargs)
        except RetryException:
            raise
        except Exception as e:
            self.logger.exception(f"An exception occured while executing {message}")
            s = StringIO()
            traceback.print_exc(file=s)
            result_body["exception"] = repr(e)
            result_body["traceback"] = s.getvalue()
        finally:
            cloudwatch.put_metric_data(
                Namespace="tclambda",
                MetricData=[
                    {
                        "MetricName": "Count",
                        "Value": 1,
                        "Unit": "Count",
                        "Dimensions": [
                            {"Name": "TcFunctionName", "Value": str(func_name)},
                            {
                                "Name": "LambdaFunctionName",
                                "Value": context.function_name,
                            },
                        ],
                    },
                    {
                        "MetricName": "RemainingMilliseconds",
                        "Value": context.get_remaining_time_in_millis(),
                        "Unit": "Milliseconds",
                        "Dimensions": [
                            {"Name": "TcFunctionName", "Value": str(func_name)},
                            {
                                "Name": "LambdaFunctionName",
                                "Value": context.function_name,
                            },
                        ],
                    },
                ],
            )

        if result_store:
            self.store_result(result_store, result_body)

    def store_result(self, key, result):
        if TC_THIS_BUCKET:
            try:
                result_body = json.dumps(result, cls=self.json_encoder_class)
            except TypeError as e:
                self.logger.exception(f"Couldn't encode result {result}")
                s = StringIO()
                traceback.print_exc(file=s)
                result_body = json.dumps(
                    {"exception": repr(e), "traceback": s.getvalue()},
                    cls=self.json_encoder_class,
                )
            s3client.put_object(Bucket=TC_THIS_BUCKET, Key=key, Body=result_body)

        return result
