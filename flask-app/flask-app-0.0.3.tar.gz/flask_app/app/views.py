from flask import Blueprint, request, Response
import json

sample_blueprint = Blueprint("user", __name__)


@sample_blueprint.route("/", methods=["GET"])
def home():
    res = json.dumps({"msg": "Hello"})
    return Response(res, 200, content_type='application/json')