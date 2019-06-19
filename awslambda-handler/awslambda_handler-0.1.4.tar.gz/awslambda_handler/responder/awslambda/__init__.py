import json
import requests

from awslambda_handler.tools import check_params_exist


class Awslambda(object):
    def __init__(self, event):
        """
        Responder to CloudFormation
        """

        # required_fields = [
        #     'ResponseURL', 'RequestType', 'StackId', 'ResourceType'
        # ]
        # check_params_exist(required_fields, event)

    def respond(self, response_data):
        """
        """
        return response_data
