import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class MultiTouch_PerformCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.MultiTouch_Perform")
    
    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "MultiTouch_Perform was successful", "MultiTouch_Perform failed")