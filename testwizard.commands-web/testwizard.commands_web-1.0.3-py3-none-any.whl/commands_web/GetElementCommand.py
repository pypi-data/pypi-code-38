import sys
import json

from testwizard.commands_core import CommandBase
from .GetElementResult import GetElementResult

class GetElement(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.GetElement")

    def execute(self, selector):
        if(selector==None):
            raise Exception("selector is required")

        requestObj = [selector]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return GetElementResult(response.read(),"GetElement was successful", "GetElement failed")