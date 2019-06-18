import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class GetCurrentWindowHandleResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)

        ResultBase.__init__(self, True if jsonObj["ok"] and jsonObj["errorCode"] == 0 else False, successMessage, failMessage)

        self.handle = jsonObj["handle"]

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])