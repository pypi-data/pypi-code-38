import sys
import json

from testwizard.commands_core import CommandBase
from .GetElementAttributeResult import GetElementAttributeResult

class GetElementAttributeCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.GetElementAttribute")
    
    def execute(self, selector, attribute):
        if(selector==None):
            raise Exception("selector is required")
        if(attribute==None):
            raise Exception("attribute is required")  
        requestObj = [selector, attribute]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        return GetElementAttributeResult(response.read(), "GetElementAttribute was successful", "GetElementAttribute failed")   