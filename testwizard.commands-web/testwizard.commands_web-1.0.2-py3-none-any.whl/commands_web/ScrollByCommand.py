import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class ScrollBy(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.ScrollBy")

    def execute(self, x, y):
        if(x==None):
            raise Exception("x is required")
        if(y==None):
            raise Exception("y is required")

        requestObj = [x, y]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"ScrollBy was successful", "ScrollBy failed")