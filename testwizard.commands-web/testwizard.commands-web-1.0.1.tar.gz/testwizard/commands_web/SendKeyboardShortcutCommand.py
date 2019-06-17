import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class SendKeyboardShortcut(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.SendKeyboardShortcut")

    def execute(self, selector, keys):
        if(selector==None):
            raise Exception("selector is required")
        if(keys==None):
            raise Exception("keys is required")

        requestObj = [selector, keys]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"SendKeyboardShortcut was successful", "SendKeyboardShortcut failed")