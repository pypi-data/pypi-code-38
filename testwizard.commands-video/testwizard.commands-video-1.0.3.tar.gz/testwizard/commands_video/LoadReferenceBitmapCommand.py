import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class LoadReferenceBitmapCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "LoadReferenceBitmap")
    
    def execute(self, filename):
        if(filename==None):
            raise Exception("filename is required")

        requestObj = [filename]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "LoadReferenceBitmap was successful", "LoadReferenceBitmap failed")