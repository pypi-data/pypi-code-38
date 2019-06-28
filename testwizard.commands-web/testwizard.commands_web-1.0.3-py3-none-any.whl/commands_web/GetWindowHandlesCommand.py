import sys
import json

from testwizard.commands_core import CommandBase
from .GetWindowHandlesResult import GetWindowHandlesResult

class GetWindowHandles(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.GetWindowHandles")

    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return GetWindowHandlesResult(response.read().decode('utf-8'),"GetWindowHandles was successful", "GetWindowHandles failed")