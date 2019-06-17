import sys
import json

from testwizard.commands_core import CommandBase
from .GetSourceResult import GetSourceResult

class GetSourceCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.GetSource")
    
    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        return GetSourceResult(response.read(), "GetSource was successful", "GetSource failed")   