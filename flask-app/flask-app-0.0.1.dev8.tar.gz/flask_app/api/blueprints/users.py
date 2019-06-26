import json

from flask import Blueprint, request

from api.blueprints.base_blueprint import BaseBluePrint
from api.controllers.user_controller import UserController

users_blueprint = Blueprint('user',__name__,url_prefix="/users")


@users_blueprint.route('/',methods=["POST","GET"])
def users():
    return UserController(request).get()