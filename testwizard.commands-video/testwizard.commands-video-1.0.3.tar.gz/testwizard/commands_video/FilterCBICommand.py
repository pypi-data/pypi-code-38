import sys
import json

from testwizard.commands_core import CommandBase
from .FilterResult import FilterResult

class FilterCBICommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "FilterCBI")
    
    def execute(self, contrast, brightness, intensity):
        if(contrast==None):
            raise Exception("contrast is required")
        if(brightness==None):
            raise Exception("brightness is required")
        if(intensity==None):
            raise Exception("intensity is required")

        requestObj = [contrast, brightness, intensity]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        
        return FilterResult(response.read(), "FilterCBI was successful", "FilterCBI failed")   