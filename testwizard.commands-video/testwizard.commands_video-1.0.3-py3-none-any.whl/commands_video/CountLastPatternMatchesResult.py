import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class CountLastPatternMatchesResult(ResultBase):
    def __init__(self, json1, successMessage, errorMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, jsonObj["matches"] != -1 and jsonObj["errorCode"] == 0, successMessage, errorMessage)

        self.matches = jsonObj["matches"]

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])