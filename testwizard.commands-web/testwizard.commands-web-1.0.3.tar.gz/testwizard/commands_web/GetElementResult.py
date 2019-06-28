import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class GetElementResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if jsonObj["ok"] else False, successMessage, failMessage)

        if("text" in jsonObj):
            self.text = jsonObj["text"]
        if("enabled" in jsonObj):
            self.enabled = jsonObj["enabled"]
        if("displayed" in jsonObj):    
            self.displayed = jsonObj["displayed"]
        if("selected" in jsonObj):    
            self.selected = jsonObj["selected"]
        if("location" in jsonObj):   
            self.location = jsonObj["location"]
        if("size" in jsonObj):   
            self.size = jsonObj["size"]

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])