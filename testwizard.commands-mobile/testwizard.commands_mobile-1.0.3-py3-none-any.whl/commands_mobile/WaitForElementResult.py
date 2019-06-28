import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class WaitForElementResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if jsonObj["elementFound"] else False, successMessage, failMessage + ": " + jsonObj["errorMessage"])

        self.time = jsonObj["time"]