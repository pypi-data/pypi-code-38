import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class TouchAction_WaitCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.TouchAction_Wait")
    
    def execute(self, duration):
        if(duration == None):
            raise Exception("duration is required")

        requestObj = [duration]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "TouchAction_Wait was successful", "TouchAction_Wait failed")