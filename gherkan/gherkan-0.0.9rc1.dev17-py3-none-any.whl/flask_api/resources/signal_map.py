from flask import jsonify, request
from flask_restful import Resource, reqparse


class SignalMap(Resource):

    def get(self, language=''):
        """
        """
        return API_FSA.requestRobotPrograms(language)

    def post(self):
        try:
            for _, value in request.files.items():
                if not language:
                    language = request.form["language"]
                API_FSA.receiveRobotPrograms(value, language)
            return {"OK": True}
        except Exception as error:
            errorMessage = f"Unable to receive the signal mappings! {error}"
            logging.exception(errorMessage)
            abort(400, message=errorMessage)

