import sys
import json

from testwizard.commands_core import CommandBase
from .WaitForElementResult import WaitForElementResult

class WaitForElementCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.WaitForElement")

    def execute(self, selector, maxSeconds):
        if(selector==None):
            raise Exception("selector is required")
        if(maxSeconds==None):
            raise Exception("maxSeconds is required")

        requestObj = [selector, maxSeconds]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return WaitForElementResult(response.read(), "WaitForElement was successful", "WaitForElement failed")