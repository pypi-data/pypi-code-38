import sys
import json

from testwizard.commands_core import CommandBase
from .GetSizeResult import GetSizeResult

class GetScreenSizeCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.GetScreenSize")
    
    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        return GetSizeResult(response.read(), "GetScreenSize was successful", "GetScreenSize failed")   