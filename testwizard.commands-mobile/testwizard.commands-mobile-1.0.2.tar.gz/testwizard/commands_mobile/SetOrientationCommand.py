import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class SetOrientationCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.SetOrientation")

    def execute(self, orientation):
        if(orientation==None):
            raise Exception("orientation is required")

        requestObj = [orientation]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "SetOrientation was successful", "SetOrientation failed")