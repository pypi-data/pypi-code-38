import sys
import json

from testwizard.commands_core import CommandBase
from .WaitForColorResult import WaitForColorResult

class WaitForColorCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "WaitForColor")
    
    def execute(self, x, y, width, height, refColor, tolerance, minSimilarity, timeout):
        if(x == None):
            raise Exception("x is required")
        if(y == None):
            raise Exception("y is required")
        if(width == None):
            raise Exception("width is required")
        if(height == None):
            raise Exception("height is required")
        if(refColor == None):
            raise Exception("refColor is required")
        if(tolerance == None):
            raise Exception("tolerance is required")
        if(minSimilarity == None):
            raise Exception("minSimilarity is required")    
        if(timeout == None):
            raise Exception("timeout is required")    

        requestObj = [x, y, width, height, refColor, tolerance, minSimilarity, timeout]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return WaitForColorResult(response.read(), "WaitForColor was successful", "WaitForColor failed")