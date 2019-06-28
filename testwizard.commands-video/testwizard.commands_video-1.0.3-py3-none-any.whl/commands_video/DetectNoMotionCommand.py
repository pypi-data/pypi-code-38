import sys
import json

from testwizard.commands_core import CommandBase
from .DetectMotionResult import DetectMotionResult

class DetectNoMotionCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "DetectNoMotion")
    
    def execute(self, x, y, width, height, minDifference, timeout, motionDuration = None, tolerance = None, distanceMethod = None, minDistance = None):
        if(x == None):
            raise Exception("x is required")
        if(y == None):
            raise Exception("y is required")
        if(width == None):
            raise Exception("width is required")
        if(height == None):
            raise Exception("height is required")
        if(minDifference == None):
            raise Exception("minDifference is required")
        if(timeout == None):
            raise Exception("timeout is required")

        requestObj = [x, y, width, height, minDifference, timeout]
        if(motionDuration != None):
            requestObj = [x, y, width, height, minDifference, timeout, motionDuration]
            if(tolerance != None):
                requestObj = [x, y, width, height, minDifference, timeout, motionDuration, tolerance]
                if(distanceMethod != None):
                    requestObj = [x, y, width, height, minDifference, timeout, motionDuration, tolerance, distanceMethod]
                    if(minDistance != None):
                        requestObj = [x, y, width, height, minDifference, timeout, motionDuration, tolerance, distanceMethod, minDistance]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return DetectMotionResult(response.read(), "DetectNoMotion was successful", "DetectNoMotion failed")