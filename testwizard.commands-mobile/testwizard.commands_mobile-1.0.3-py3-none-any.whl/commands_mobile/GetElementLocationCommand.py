import sys
import json

from testwizard.commands_core import CommandBase
from .GetElementLocationResult import GetElementLocationResult

class GetElementLocationCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.GetElementLocation")
    
    def execute(self, selector):
        if(selector==None):
            raise Exception("selector is required")
        requestObj = [selector]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        return GetElementLocationResult(response.read(), "GetElementLocation was successful", "GetElementLocation failed")   