import sys
import json

from testwizard.commands_core import CommandBase
from .FilterResult import FilterResult

class FilterColorBlackWhiteCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "FilterColorBlackWhite")
    
    def execute(self, color, tolerance):
        if(color==None):
            raise Exception("color is required")
        if(tolerance==None):
            raise Exception("tolerance is required")

        requestObj = [color, tolerance]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return FilterResult(response.read(), "FilterColorBlackWhite was successful", "FilterColorBlackWhite failed")   