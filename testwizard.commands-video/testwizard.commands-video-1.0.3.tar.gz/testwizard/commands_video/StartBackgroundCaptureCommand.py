import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class StartBackgroundCaptureCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "StartBGCapture")
    
    def execute(self, stepSize, captures):
        if(stepSize==None):
            raise Exception("stepSize is required")
        if(captures==None):
            raise Exception("captures is required")

        requestObj = [stepSize, captures]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "StartBackgroundCapture was successful", "StartBackgroundCapture failed")