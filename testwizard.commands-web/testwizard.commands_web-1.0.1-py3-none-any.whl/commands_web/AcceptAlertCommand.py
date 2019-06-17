import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class AcceptAlert(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.AcceptAlert")

    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"acceptAlert was successful", "acceptAlert failed")