import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class Android_SendKeyCodeCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.Android_SendKeyCode")
    
    def execute(self, keyCode):
        
        if(keyCode == None):
            raise Exception("keyCode is required")
        
        requestObj = [keyCode]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        
        return SimpleResult(response.read(), "Android_SendKeyCode was successful", "Android_SendKeyCode failed")   