import sys
import json

from testwizard.commands_core import CommandBase
from .GetChildrenResult import GetChildrenResult

class GetChildren(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.GetChildren")

    def execute(self, selector):
        if(selector==None):
            raise Exception("selector is required")

        requestObj = [selector]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return GetChildrenResult(response.read().decode('utf-8'),"GetChildren was successful", "GetChildren failed")