import sys
import json

from testwizard.commands_core import CommandBase
from .GetCurrentWindowHandleResult import GetCurrentWindowHandleResult

class GetCurrentWindowHandle(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.GetCurrentWindowHandle")

    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return GetCurrentWindowHandleResult(response.read().decode('utf-8'),"GetCurrentWindowHandle was successful", "GetCurrentWindowHandle failed")