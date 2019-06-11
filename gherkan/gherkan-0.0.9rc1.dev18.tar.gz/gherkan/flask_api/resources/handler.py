from flask import jsonify, request, Response
from flask_restful import Resource, reqparse, abort
import re
from .. import API_FSA
import logging


class Handler(Resource):
    A_RESET = "reset"
    A_SET_RESPONSE_MODE = "set_response_mode"

    def get(self, action, param=None):
        if action == self.A_RESET:
            API_FSA.regenerateConfig()
            API_FSA.setState(API_FSA.S_IDLE)
        elif action == self.A_SET_RESPONSE_MODE:
            API_FSA.setConfig(API_FSA.P_RESPONSE_MODE, param)
        else:
            errorMessage = "Requested action is not defined! Requested action: '{}'".format(str(action))
            logging.error(errorMessage)
            abort(405, message=errorMessage)

        return {"OK": True}