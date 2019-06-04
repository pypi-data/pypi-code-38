from flask import Response
import json


class CustomResponse(Response):
    def __init__(self, data={}, status_code=200, message="OK", **kwargs):
        response_object = {}
        try:
            response_object["status code"] = int(status_code)
        except ValueError:
            raise ValueError("invalid literal for int() with base 10")
        try:
            data = json.loads(data)
            raise ValueError("Data send in json format. Please use the right format")
        except Exception as e:
            pass
        if isinstance(data, str) or isinstance(data, unicode):
            response_object["message"] = str(data)
            response_object["data"] = {}
        elif isinstance(data, dict) or isinstance(data, list):
            response_object["message"] = message
            response_object["data"] = data
        else:
            raise ValueError("Unsupported Data Structure: We only except string, dictionary and list")

        if 'content_type' not in kwargs:
            kwargs['content_type'] = "application/json"

        return super(CustomResponse, self).__init__(response=json.dumps(response_object), status=int(status_code), **kwargs)