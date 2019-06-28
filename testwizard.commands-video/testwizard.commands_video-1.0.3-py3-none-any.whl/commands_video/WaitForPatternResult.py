import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class WaitForPatternResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, False if jsonObj["time"] != -1 and jsonObj["errorCode"] != 0 else True, successMessage, failMessage)

        self.time = jsonObj["time"]
        self.similarity = jsonObj["similarity"]
        self.position = jsonObj["position"]

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])