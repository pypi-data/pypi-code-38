from flask import jsonify, request, Response, make_response
from flask_restful import Resource, reqparse, abort
import re
from .. import API_FSA
import logging


class Signals(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("language", type=str, choices=("en", "cs"), required=True)
    parser.add_argument("background", type=str)
    parser.add_argument("description", type=str)
    parser.add_argument("scenarios", action="append", required=True)

    langDirRegex = re.compile("^.*#\s*lang\w*\s*:.+$", re.IGNORECASE | re.MULTILINE)

    def __init__(self, remap=False):
        self.remap = remap

    def get(self):
        # Check if NL text was received and processed
        if API_FSA.canRequestSignal():
            if self.remap:
                # request remapped signal file
                response = API_FSA.requestRemappedSignal()
            else:
                # request signal file
                response = API_FSA.requestSignal()
            return response
        else:
            errorMessage = "It is not possible to request a signal file. Most likely no NL text was provided"
            logging.error(errorMessage)
            abort(406, message="It is not possible to request a signal file. Most likely no NL text was provided")

    def post(self):
        """
        request = {
                "language": "en<OR>cs",
                "background": "background text",
                "description": "optional description",
                "scenarios": [
                    "scenario1 signal text",
                    "scenario2 signal text"
                ]
        }
        """
        # A signal file arrived
        args = self.parser.parse_args()
        fileText = '\n'.join(args["scenarios"])

        # TODO: better text file composition

        if args["background"] is not None:
            fileText = '\n'.join([args["background"], fileText])

        # if self.langDirRegex.search(fileText) is None:
        #     # Add language directive if it is not in the text
        #     fileText = '\n'.join([args["language"], fileText])
        try:
            API_FSA.receiveSignal(fileText)
        except Exception as error:
            errorMessage = "An error occurred while processing the signals! Error: '{}'".format(str(error))
            logging.exception(errorMessage)
            abort(406, message=errorMessage)

        return {"OK": True}




class NegatedSignals(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("language", type=str, choices=("en", "cs"), required=True)
    parser.add_argument("background", type=str)
    parser.add_argument("description", type=str)
    parser.add_argument("scenarios", action="append", required=True)

    langDirRegex = re.compile("^.*#\s*lang\w*\s*:.+$", re.IGNORECASE | re.MULTILINE)

    def get(self):
        # Check if NL text was received and processed
        if API_FSA.canRequestNegatedSignal():
            # request signal file
            response = API_FSA.requestNegatedSignal()
            return response
        else:
            errorMessage = "It is not possible to request a signal file. Most likely no NL text was provided"
            logging.error(errorMessage)
            abort(406, message="It is not possible to request a signal file. Most likely no NL text was provided")

    def post(self):
        errorMessage = "Error: Negated signals cannot be posted."
        logging.error(errorMessage)
        abort(406, message=errorMessage)