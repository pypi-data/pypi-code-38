from flask_restplus import Namespace, Resource, fields
from flask import request, jsonify

import time
import uuid

from strongr.core.domain.secretdomain import SecretDomain
from strongr.restdomain.api.utils import namespace_require_oauth


ns = Namespace('secrets', description='Operations related to the secretsdomain')

@ns.route('/')
class ListSecrets(Resource):
    def __init__(self, *args, **kwargs):
        super(ListSecrets, self).__init__(*args, **kwargs)

    @ns.response(200, '')
    def get(self):
        secret_service = SecretDomain.secret_service()
        secret_query_factory = SecretDomain.query_factory()

        secret_query_bus = secret_service.get_query_bus()

        result = secret_query_bus.handle(secret_query_factory.new_list_secrets())

        return result, 200

@ns.route('/<string:key>/<string:value>')
class PostSecret(Resource):
    def __init__(self, *args, **kwargs):
        super(PostSecret, self).__init__(*args, **kwargs)

    @ns.response(201, 'Secret successfully created.')
    def post(self, key, value):
        secret_service = SecretDomain.secret_service()
        secret_command_factory = SecretDomain.command_factory()

        secret_command_bus = secret_service.get_command_bus()

        secret_command_bus.handle(secret_command_factory.new_add_secret(key, value))

        return {'key': key}, 200

@ns.route('/<string:key>')
class DeleteSecret(Resource):
    def __init__(self, *args, **kwargs):
        super(DeleteSecret, self).__init__(*args, **kwargs)

    @ns.response(202, 'Secret successfully deleted.')
    def delete(self, key):
        secret_service = SecretDomain.secret_service()
        secret_command_factory = SecretDomain.command_factory()

        secret_command_bus = secret_service.get_command_bus()

        secret_command_bus.handle(secret_command_factory.new_remove_secret(key))

        return {'key': key}, 201

