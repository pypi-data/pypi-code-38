import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class FindPatternResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        self.similarity = jsonObj["similarity"]
        self.position = jsonObj["position"]
        ResultBase.__init__(self, False if self.similarity!= -1 and jsonObj["errorCode"] == 0 else True, successMessage, failMessage)

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])