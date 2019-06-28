import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class GetUrlResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if jsonObj["ok"] and jsonObj["errorCode"] == 0 else False, successMessage, failMessage)

        self.url = jsonObj["url"]
        self.message = jsonObj["message"]

        if(self.success):
            return

        self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])