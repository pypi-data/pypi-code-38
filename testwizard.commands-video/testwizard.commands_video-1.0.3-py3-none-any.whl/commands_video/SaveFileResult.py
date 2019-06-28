import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class SaveFileResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        if("saved" in jsonObj):
            jsonObj["ok"] = jsonObj["saved"]
        self.filePath = jsonObj["generatedFilename"]
        ResultBase.__init__(self, True if jsonObj["ok"] else False, successMessage, failMessage)

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])
        else:
            self.message = self.message + jsonObj["errorMessage"]