import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class StartWebDriver(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.StartWebDriver")

    def execute(self, browser = None, serverUrl = None):
        requestObj = []
        if(browser is not None):
            requestObj = [browser]
            if(serverUrl is not None):
                requestObj = [browser,serverUrl]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"StartWebDriver was successful", "StartWebDriver failed")