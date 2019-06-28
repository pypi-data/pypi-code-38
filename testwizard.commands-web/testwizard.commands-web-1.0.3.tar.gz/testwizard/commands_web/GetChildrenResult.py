import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class GetChildrenResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if jsonObj["ok"] and jsonObj["errorCode"] == 0 else False, successMessage, failMessage)

        if("numberOfElements" in jsonObj):
            self.numberOfElements = jsonObj["numberOfElements"]
        if("elements" in jsonObj):
            self.elements = jsonObj["elements"]
        if("message" in jsonObj):
            failMessage = jsonObj["message"]

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])