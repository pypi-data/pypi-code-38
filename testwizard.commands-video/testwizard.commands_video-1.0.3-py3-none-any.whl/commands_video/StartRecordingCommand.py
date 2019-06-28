import sys
import json

from testwizard.commands_core import CommandBase
from .SaveFileResult import SaveFileResult

class StartRecordingCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "StartRecording")
    
    def execute(self, filename):
        if(filename==None):
            raise Exception("filename is required")

        requestObj = [filename]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SaveFileResult(response.read(), "StartRecording was successful", "StartRecording failed")