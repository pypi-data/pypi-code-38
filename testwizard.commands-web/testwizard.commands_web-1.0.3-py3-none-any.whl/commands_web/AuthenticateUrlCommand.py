import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class AuthenticateUrl(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.AuthenticateUrl")

    def execute(self, username, password, link):
        if(username==None):
            raise Exception("username is required")
        if(password==None):
            raise Exception("password is required")
        if(link==None):
            raise Exception("link is required")

        requestObj = [username, password, link]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"AuthenticateUrl was successful", "AuthenticateUrl failed")