import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class ClickPositionCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.ClickPosition")

    def execute(self, x, y):
        if(x==None):
            raise Exception("x is required")
        if(y==None):
            raise Exception("y is required")

        requestObj = [x, y]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "ClickPosition was successful", "ClickPosition failed")