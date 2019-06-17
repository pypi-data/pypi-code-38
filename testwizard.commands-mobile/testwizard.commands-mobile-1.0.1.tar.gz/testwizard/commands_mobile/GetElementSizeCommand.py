import sys
import json

from testwizard.commands_core import CommandBase
from .GetSizeResult import GetSizeResult

class GetElementSizeCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.GetElementSize")
    
    def execute(self, selector):
        if(selector==None):
            raise Exception("selector is required")
        requestObj = [selector]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        return GetSizeResult(response.read(), "GetElementSize was successful", "GetElementSize failed")   