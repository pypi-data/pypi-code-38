from functools import wraps

import json


__version__ = '1.0.2'
__author__ = 'Tripleko LLC'
__author_email__ = 'jared@tripleko.com'
__description__ = 'Baby Hatano'


class Request:
    def __init__(self, params={}, data=b"", headers={}, multi={}, pathparams={}):
        self.params = params
        self.data = data
        self.headers = headers
        self.multi = multi
        self.pathparams = pathparams


class KotanoError(Exception):
    pass


def proxy(typ):
    def create_proxy(inner):
        @wraps(inner)
        def wrapped(*args, **kwargs):
            if len(args) != 2:
                raise KotanoError(
                        f"Number of args: {len(args)} (should be 2)")
            assert len(args) == 2
            event, context = args
            if not isinstance(event, dict):
                raise KotanoError("Function called in improper context")

            data = event.get('body', b"")
            params = event.get('queryStringParameters', {})
            headers = event.get('headers', {})
            pathparams = event.get('pathParameters', {})
            multi = event.get('multiValueQueryStringParameters', {})
            req = Request(
                    params=params,
                    data=data,
                    headers=headers,
                    multi=multi,
                    pathparams=pathparams)
            body = inner(req)
            if not isinstance(body, str):
                body = json.dumps(body)
            if typ == 'api':
                return {
                        'statusCode': 200,
                        'body': body}
            elif typ == 'html':
                return {
                        'statusCode': 200,
                        'body': body,
                        'headers': {
                            'Content-type': 'text/html'
                            }
                        }
        return wrapped
    return create_proxy

