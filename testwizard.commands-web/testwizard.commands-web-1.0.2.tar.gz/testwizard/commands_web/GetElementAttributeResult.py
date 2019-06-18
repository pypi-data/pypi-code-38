import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class GetElementAttributeResult(ResultBase):
    def __init__(self, Json, successMessage, failMessage):
        jsonObj = json.loads(Json)
        ResultBase.__init__(self, True if jsonObj["ok"] and jsonObj["errorCode"] == 0 else False, successMessage, failMessage)

        self.value = jsonObj["value"]

        if(self.success):
            return

        self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])