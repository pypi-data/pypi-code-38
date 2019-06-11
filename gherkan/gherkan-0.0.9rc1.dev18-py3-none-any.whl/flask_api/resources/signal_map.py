from flask import jsonify, request
from flask_restful import Resource, reqparse, abort
from .. import API_FSA
import logging


class SignalMap(Resource):

    def get(self, language='en'):
        """
        """
        return API_FSA.requestSignalMapping(language)

    def post(self, language='en'):
        try:
            for _, value in request.files.items():
                if not language:
                    language = request.form["language"]
                API_FSA.receiveSignalMapping(value, language)
            return {"OK": True}
        except Exception as error:
            errorMessage = f"Unable to receive the signal mappings! {error}"
            logging.exception(errorMessage)
            abort(400, message=errorMessage)

