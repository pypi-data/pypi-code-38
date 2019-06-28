import sys
import json

from testwizard.commands_core import CommandBase
from .FilterResult import FilterResult

class FilterBlackWhiteCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "FilterBlackWhite")
    
    def execute(self, separation):
        
        if(separation==None):
            raise Exception("separation is required")

        requestObj = [separation]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        
        return FilterResult(response.read(), "FilterBlackWhite was successful", "FilterBlackWhite failed")   