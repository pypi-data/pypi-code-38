import sys
import json

from testwizard.commands_core import CommandBase
from .FindPatternResult import FindPatternResult

class FindPatternCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "FindPattern")
    
    def execute(self, filename, mode):
        if(filename==None):
            raise Exception("filename is required")
        if(mode==None):
            raise Exception("mode is required")

        requestObj = [filename, mode]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")        

        return FindPatternResult(response.read(), "FindPattern was successful", "FindPattern failed")   