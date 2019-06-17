import sys
import json

from testwizard.commands_core import CommandBase
from .GetElementAttributeResult import GetElementAttributeResult

class GetElementAttribute(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.GetElementAttribute")
    
    def execute(self, selector, name):
        if(selector==None):
            raise Exception("selector is required")
        if(name==None):
            raise Exception("name is required")

        requestObj = [selector, name]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return GetElementAttributeResult(response.read().decode('utf-8'),"GetElementAttribute was successful", "GetElementAttribute failed")