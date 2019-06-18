import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class MultiAction_DoubleClick(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.MultiAction_DoubleClick")

    def execute(self, selector):
        if(selector==None):
            raise Exception("selector is required")

        requestObj = [selector]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"MultiAction_DoubleClick was successful", "MultiAction_DoubleClick failed")