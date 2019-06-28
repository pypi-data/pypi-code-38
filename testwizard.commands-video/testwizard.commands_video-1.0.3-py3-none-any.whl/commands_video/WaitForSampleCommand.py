import sys
import json

from testwizard.commands_core import CommandBase
from .WaitForSampleResult import WaitForSampleResult

class WaitForSampleCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "WaitForSample")
    
    def execute(self, x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod = None, maxDistance = None):
        if(x == None):
            raise Exception("x is required")
        if(y == None):
            raise Exception("y is required")
        if(width == None):
            raise Exception("width is required")
        if(height == None):
            raise Exception("height is required")
        if(minSimilarity == None):
            raise Exception("minSimilarity is required")
        if(timeout == None):
            raise Exception("timeout is required")
        if(tolerance == None):
            raise Exception("tolerance is required")
        requestObj = [x, y, width, height, minSimilarity, timeout, tolerance]

        if(distanceMethod != None):
            requestObj = [x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod]
            if(maxDistance!= None):
                requestObj = [x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod, maxDistance]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return WaitForSampleResult(response.read(), "WaitForSample was successful", "WaitForSample failed")