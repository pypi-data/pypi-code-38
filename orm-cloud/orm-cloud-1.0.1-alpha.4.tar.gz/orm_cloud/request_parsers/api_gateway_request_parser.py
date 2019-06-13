import json


class ApiGatewayRequestParser:
    def __init__(self):
        pass

    def parse(self, request):
        request_json = json.loads(request)

        resource = request_json['resource']
        path = request_json['path']
        action = request_json['httpMethod']
        query_string_params = request_json['queryStringParameters']
        headers = request_json['headers']

        return {
            'resource': resource,
            'path': path,
            'action': action,
            'query_string_params': query_string_params,
            'headers': headers
        }
