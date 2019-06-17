import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class SendKeys(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.SendKeys")

    def execute(self, selector, text):
        if(selector==None):
            raise Exception("selector is required")
        if(text==None):
            raise Exception("text is required")

        requestObj = [selector, text]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"SendKeys was successful", "SendKeys failed")