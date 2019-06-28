import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class GoToUrl(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.GoToUrl")

    def execute(self, url):
        if(url==None):
            raise Exception("url is required")

        requestObj = [url]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read().decode('utf-8'),"GoToUrl was successful", "GoToUrl failed")