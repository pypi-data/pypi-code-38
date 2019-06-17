import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class AddArgument(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.AddArgument")

    def execute(self, argument):
        if(argument==None):
            raise Exception("argument is required")

        requestObj = [argument]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(),"AddArgument was successful", "AddArgument failed")