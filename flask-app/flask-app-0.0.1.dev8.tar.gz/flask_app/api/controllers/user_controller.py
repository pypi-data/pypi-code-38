import json

from flask import Response


class UserController(object):

    def __init__(self, request, *args, **kwargs):
        self.request = request

    def get(self, *args, **kwargs):
        return Response(json.dumps({'message': 'Hello'}),
                        content_type="application/json")

    def post(self, *args, **kwargs):
        pass

    def put(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass
