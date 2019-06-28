import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class CompareResult(ResultBase):
    def __init__(self, json1 , successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, False if self.similarity!= -1 and jsonObj["similarity"] == 0 else True, successMessage, failMessage)

        self.similarity = jsonObj["similarity"]

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])