import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class ScreenshotResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        if("saved" in jsonObj):
            jsonObj["ok"] = jsonObj["saved"]
        ResultBase.__init__(self, True if jsonObj["ok"] else False, successMessage, failMessage)

        self.filePath = jsonObj["generatedFilename"]

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])
        else:
            self.message = self.message + jsonObj["errorMessage"]