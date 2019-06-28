import sys
import json

from testwizard.commands_core import CommandBase
from .GetUrlResult import GetUrlResult

class GetUrl(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.GetUrl")

    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return GetUrlResult(response.read().decode('utf-8'),"GetUrl was successful", "GetUrl failed")