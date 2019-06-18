import sys
import json

from testwizard.commands_core.ResultBase import ResultBase

class GetSourceResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if jsonObj["ok"] else False, successMessage, failMessage + ": " + jsonObj["errorMessage"])

        self.source = jsonObj["source"]
