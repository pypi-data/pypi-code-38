import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class TouchAction_MoveToElementCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.TouchAction_MoveToElement")

    def execute(self, selector):
        if(selector==None):
            raise Exception("selector is required")

        requestObj = [selector]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "TouchAction_MoveToElement was successful", "TouchAction_MoveToElement failed")