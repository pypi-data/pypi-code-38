from flask import jsonify, request
from flask_restful import Resource, reqparse, abort
from .. import API_FSA
import logging


class SignalMap(Resource):

    def get(self, language='en'):
        """
        """
        try:
            return API_FSA.requestSignalMapping(language)
        except Exception as error:
            errorMessage = f"Unable to retreive the signal mappings! {error}"
            logging.exception(errorMessage)
            abort(400, message=errorMessage)

    def post(self, language='en'):
        try:
            requestHadFile = False
            for _, value in request.files.items():
                if not language:
                    language = request.form["language"]
                API_FSA.receiveSignalMapping(value, language)
                requestHadFile = True
            if requestHadFile:
                return {"OK": True}
            else:
                errorMessage = f"Signal mapping was sent but the request contained no file!"
                logging.exception(errorMessage)
                abort(400, message=errorMessage)
        except Exception as error:
            errorMessage = f"Unable to receive the signal mappings! {error}"
            logging.exception(errorMessage)
            abort(400, message=errorMessage)

