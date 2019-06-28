
import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class HideKeyboardCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.HideKeyboard")
    
    def execute(self, iOS_Key = None):
        requestObj = []
        if(iOS_Key!=None):
            requestObj = [iOS_Key]
        requestObj = json.dumps(requestObj)
        response = self.robot.post(self.url, requestObj, "Could not execute command")
        
        return SimpleResult(response.read(), "HideKeyboard was successful", "HideKeyboard failed")   