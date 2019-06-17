import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class MultiAction_SendKeys(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.MultiAction_Sendkeys")

    def execute(self, inputString, selector = None):
        if(inputString==None):
            raise Exception("inputString is required")

        requestObj = [inputString]
        if(selector != None):
            requestObj = [selector, inputString]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"MultiAction_SendKeys was successful", "MultiAction_SendKeys failed")