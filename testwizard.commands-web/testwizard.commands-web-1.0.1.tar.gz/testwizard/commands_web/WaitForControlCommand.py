import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class WaitForControl(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.WaitForControl")

    def execute(self, selector, seconds):
        if(selector==None):
            raise Exception("selector is required")
        if(seconds==None):
            raise Exception("seconds is required")

        requestObj = [selector, seconds]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"WaitForControl was successful", "WaitForControl failed")