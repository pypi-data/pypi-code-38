# -*- coding: utf-8 -*-
from flask import jsonify, request, Response
from flask_restful import Resource, reqparse, abort
from .. import API_FSA
import logging


class NLText(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("feature", type=str, default="Robot")
    parser.add_argument("feature_desc", type=str, default="")
    parser.add_argument("language", type=str, choices=("en", "cs"), required=True)
    parser.add_argument("background", type=str)
    parser.add_argument("text_raw", type=str, required=True)

    def get(self):
        if API_FSA.canRequestNLText():
            response = API_FSA.requestNLText()
            return response
        else:
            errorMessage = "NL text cannot be requested!"
            logging.error(errorMessage)
            abort(406, message=errorMessage)

    def post(self):
        args = self.parser.parse_args()

        try:
            response = API_FSA.receiveNLText(args)
        except Exception as error:
            errorMessage = "An error occurred while processing the NL text! Error: '{}'".format(str(error))
            logging.exception(errorMessage)
            abort(406, message=errorMessage)
        else:
            return response
