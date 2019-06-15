import calendar
import random

import itertools
import time
from gaia_python_sdk_api.transporter.abstract_transporter import ITransporter

from .atlas_request import AtlasRequest
from .atlas_response import AtlasResponse


class AtlasClient(object):
    """
    This class represents the service facade for ATLAS functions.
    """

    def __init__(self, transporter: ITransporter):
        self.transporter = transporter
        self.counter = itertools.count(random.randint(0, 1000000))

    def execute_native(self, statement, variables, preprocessors):
        payload = {
            "statement": statement,
            "variables": variables,
            "timestamp": calendar.timegm(time.gmtime()),
            "nonce": self.counter.__next__(),
            "preprocessors": preprocessors
        }

        return AtlasResponse(self.transporter.transport(payload))

    def execute(self, request: AtlasRequest):
        statement = "query atlas($text: String!, $merge: Boolean!) { ver nlu(text: $text, merge: $merge) { " + (
            " ".join(request)) + "}}"
        variables = {"text": request.text, "merge": request.merge}

        return self.execute_native(statement, variables, [])
