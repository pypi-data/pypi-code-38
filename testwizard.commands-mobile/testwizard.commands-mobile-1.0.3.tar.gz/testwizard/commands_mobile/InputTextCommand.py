import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class InputTextCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.InputText")
    
    def execute(self, selector, text):
        
        if(selector==None):
            raise Exception("selector is required")
        if(text==None):
            raise Exception("text is required")
        requestObj = [selector, text]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        
        return SimpleResult(response.read(), "InputText was successful", "InputText failed")   