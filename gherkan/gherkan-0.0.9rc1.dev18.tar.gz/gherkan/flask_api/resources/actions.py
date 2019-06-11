from flask import jsonify, request
from flask_restful import Resource, reqparse, abort
from .. import API_FSA
import logging

class Actions(Resource):
    parser = reqparse.RequestParser()

    def get(self, language=''):
        return API_FSA.requestRobotPrograms(language)

    def post(self, language=''):
        try:
            for _, value in request.files.items():
                if not language:
                    language = request.form["language"]
                API_FSA.receiveRobotPrograms(value, language)
            return {"OK": True}
        except Exception as error:
            errorMessage = f"Unable to receive the robot programs! {error}"
            logging.exception(errorMessage)
            abort(400, message=errorMessage)
