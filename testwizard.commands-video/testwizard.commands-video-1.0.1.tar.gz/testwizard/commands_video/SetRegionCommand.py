import sys
import json

from testwizard.commands_core import CommandBase
from .FilterResult import FilterResult

class SetRegionCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "SetRegion")

    def execute(self, x, y, width, height):
        if(x==None):
            raise Exception("x is required")
        if(y==None):
            raise Exception("y is required")
        if(width==None):
            raise Exception("width is required")
        if(height==None):
            raise Exception("height is required")

        requestObj = [x, y, width, height]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return FilterResult(response.read(), "SetRegion was successful", "SetRegion failed")