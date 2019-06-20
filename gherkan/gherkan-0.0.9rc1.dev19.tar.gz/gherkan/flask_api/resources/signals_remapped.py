from flask import jsonify, request, Response, make_response
from flask_restful import Resource, reqparse, abort
import re
from .. import API_FSA
import logging


class SignalsRemapped(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("language", type=str, choices=("en", "cs"), required=True)
    parser.add_argument("background", type=str)
    parser.add_argument("description", type=str)
    parser.add_argument("scenarios", action="append", required=True)

    langDirRegex = re.compile("^.*#\s*lang\w*\s*:.+$", re.IGNORECASE | re.MULTILINE)

    def get(self):
        # Check if NL text was received and processed
        # request remapped signal file
        logging.info("Requested remapped signals.")
        response = API_FSA.requestRemappedSignal()
        return response
