import base64
import functools
import json
import os


class Request(object):
    def __init__(self, **kwargs):
        self.method = None
        self.headers = None
        self.body = None
        self.path_params = None
        self.query_params = None
        self.content_type = None
        self.content_params = None
        self.user = None

    def __setattr__(self, name, value):
        return super().__setattr__(name, value)


def aws_http_event_to_request(event, context):
    request = Request()
    request.method = event["httpMethod"].upper()
    request.headers = event["headers"]
    request.content_type = request.headers.get("Content-Type", None)
    request.path_params = event.get("pathParameters", None)

    body = event["body"]

    if isinstance(body, str) and body == "":
        body = None

    if body is not None:
        is_request_body_encoded = event.get("isBase64Encoded", False)
        if is_request_body_encoded:
            decoded = base64.b64decode(body)
            body = json.loads(decoded)
        else:
            body = json.loads(body)
    request.body = body
    request.query_params = event["queryStringParameters"]
    return request


def handler(provider=None):
    assert isinstance(provider, (str, type(None))), "Expected provider to be string"

    def inner(method_func):
        @functools.wraps(method_func)
        def _handle(*args, **kwargs):
            nonlocal provider
            if provider is None:
                # ?  Should the default be aws lambda
                provider = os.getenv("STOCKIST_PROVIDER", "AWS")

            provider = provider.upper()

            if provider == "AWS":
                event, context = args
                request = aws_http_event_to_request(event, context)
                return method_func(request)

            raise NotImplementedError("FaaS provider not supported")

        return _handle

    return inner
