import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class GetWindowHandlesResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if jsonObj["ok"] and jsonObj["errorCode"] == 0 else False, successMessage, failMessage)

        if("numberOfElements" in jsonObj):
            self.numberOfHandles = jsonObj["numberOfElements"]
        if("elements" in jsonObj):
            self.handles = jsonObj["elements"]

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])