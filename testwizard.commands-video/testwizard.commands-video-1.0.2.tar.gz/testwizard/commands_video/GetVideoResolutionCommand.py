import sys
import json

from testwizard.commands_core import CommandBase
from .GetVideoResolutionResult import GetVideoResolutionResult

class GetVideoResolutionCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "GetVideoResolution")
    
    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return GetVideoResolutionResult(response.read(), "GetVideoResolution was successful", "GetVideoResolution failed")