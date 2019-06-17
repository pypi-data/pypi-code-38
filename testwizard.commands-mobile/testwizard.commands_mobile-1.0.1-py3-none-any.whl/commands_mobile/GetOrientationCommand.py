import sys
import json

from testwizard.commands_core import CommandBase
from .GetOrientationResult import GetOrientationResult

class GetOrientationCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.GetOrientation")
    
    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        return GetOrientationResult(response.read(), "GetOrientation was successful", "GetOrientation failed")   