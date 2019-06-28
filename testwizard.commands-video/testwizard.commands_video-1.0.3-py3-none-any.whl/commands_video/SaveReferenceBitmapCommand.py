import sys
import json

from testwizard.commands_core import CommandBase
from .SaveFileResult import SaveFileResult

class SaveReferenceBitmapCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "SaveReferenceBitmap")
    
    def execute(self, filename):
        if(filename==None):
            raise Exception("filename is required")

        requestObj = [filename]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SaveFileResult(response.read(), "SaveReferenceBitmap was successful", "SaveReferenceBitmap failed")