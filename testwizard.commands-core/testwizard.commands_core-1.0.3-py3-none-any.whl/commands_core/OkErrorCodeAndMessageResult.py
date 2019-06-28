import json
import sys

from .ResultBase import ResultBase

class OkErrorCodeAndMessageResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if jsonObj["ok"] else False, successMessage, failMessage)

        if(self.success):
            return
        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])