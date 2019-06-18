import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class AddChromeExtension(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.AddChromeExtension")

    def execute(self, filepath):
        if(filepath==None):
            raise Exception("filepath is required")

        requestObj = [filepath]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(),"AddChromeExtension was successful", "AddChromeExtension failed")