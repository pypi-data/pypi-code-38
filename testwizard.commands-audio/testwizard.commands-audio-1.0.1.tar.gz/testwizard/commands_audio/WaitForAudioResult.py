import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class WaitForAudioResult(ResultBase):
    def __init__(self, json1 , successMessage, failMessage):
        jsonObj = json.loads(json1)
        self.rightLevel = jsonObj["rightLevel"]
        self.leftLevel = jsonObj["leftLevel"]
        self.time = jsonObj["time"]
        ResultBase.__init__(self, True if self.time>=1 else False, successMessage, failMessage)

        if(self.success):
            return
        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])