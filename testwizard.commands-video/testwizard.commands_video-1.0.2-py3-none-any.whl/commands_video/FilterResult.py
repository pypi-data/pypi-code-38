import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class FilterResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        self.success = jsonObj["ok"]
        ResultBase.__init__(self, jsonObj["ok"], successMessage, failMessage)

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])