import sys

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

import json
class InitDriverCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.InitDriver")
    
    def execute(self, appPath):
        
        if(appPath):
            requestObj = [appPath]
        else:
            requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        
        return SimpleResult(response.read(), "InitDriver was successful", "InitDriver failed")   