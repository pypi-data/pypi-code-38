from flask import jsonify, request
from flask_restful import Resource, reqparse
from .. import API_FSA

class NLScenario(Resource):

    def get(self):
        """
        response = {
                "language":"en<OR>cz",
                "background": "background text",
                "description": "optional description",
                "scenarios": [
                    "scenario1 NL text",
                    "scenario2 NL text"
                ]
        }
        """
        pass

