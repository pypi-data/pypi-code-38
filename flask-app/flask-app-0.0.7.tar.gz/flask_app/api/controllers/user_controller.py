import json

from flask import Response

from api.controllers.base_controller import BaseController


class UserController(BaseController):

    def get(self, *args, **kwargs):
        return Response(json.dumps({'message': 'Hello'}),
                        content_type="application/json")

    def post(self, *args, **kwargs):
        pass