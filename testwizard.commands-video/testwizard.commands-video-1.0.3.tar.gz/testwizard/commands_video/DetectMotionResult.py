import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class DetectMotionResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, jsonObj["time"] != -1 and jsonObj["errorCode"] == 0, successMessage, failMessage)

        self.time = jsonObj["time"]
        self.difference = jsonObj["difference"]
        self.distance = jsonObj["distance"]

        if(self.success):
            return
        
        if(jsonObj["errorCode"] == 14):
            self.message = self.message + ": motionDuration is bigger than Timeout"
        else:
            if("errorCode" in jsonObj):
                self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])