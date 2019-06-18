import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class MultiAction_MoveToElementOffset(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.MultiAction_MoveToElementOffset")

    def execute(self, selector, xOffset, yOffset):
        if(selector==None):
            raise Exception("selector is required")
        if(xOffset==None):
            raise Exception("xOffset is required")
        if(yOffset==None):
            raise Exception("yOffset is required")

        requestObj = [selector, xOffset, yOffset]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"MultiAction_MoveToElementOffset was successful", "MultiAction_MoveToElementOffset failed")