import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class SwitchPowerCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "SwitchPower")
    
    def execute(self, on):
        if(on == None):
            raise Exception("on is required")

        requestObj = [on]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "SwitchPower was successful", "SwitchPower failed")