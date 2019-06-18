import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class WaitForColorResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, False if jsonObj["time"] != -1 and jsonObj["errorCode"] != 0 else True, successMessage, failMessage)

        self.time = jsonObj["time"]
        self.similarity = jsonObj["similarity"]
        if("color" in jsonObj):
            rgbValues = jsonObj["color"].split(',')
            self.color = Color(rgbValues[1], rgbValues[2], rgbValues[3])

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])

class Color(object):
    def __init__(self, r, g, b):
       self.r = int(r)
       self.g = int(g)
       self.b = int(b)