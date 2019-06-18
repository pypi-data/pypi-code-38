import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class GetElementLocationResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if jsonObj["ok"] else False, successMessage, failMessage + ": " + jsonObj["errorMessage"])

        self.x = jsonObj["x"]
        self.y = jsonObj["y"]