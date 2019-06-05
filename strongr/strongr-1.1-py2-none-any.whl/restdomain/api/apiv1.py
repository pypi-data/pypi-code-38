from flask import Blueprint
from flask_restplus import Api

from strongr.restdomain.api.v1.scheduler import ns as scheduler_namespace
from strongr.restdomain.api.v1.oauth2 import ns as oauth2_namespace
from strongr.restdomain.api.v1.secrets import ns as secrets_namespace

blueprint = Blueprint('api_v1', __name__, url_prefix='/v1')
api = Api(blueprint,
    title='V1 Api',
    version='1.0',
    description='First version of the API'
)

api.add_namespace(scheduler_namespace)
api.add_namespace(oauth2_namespace)
api.add_namespace(secrets_namespace)
