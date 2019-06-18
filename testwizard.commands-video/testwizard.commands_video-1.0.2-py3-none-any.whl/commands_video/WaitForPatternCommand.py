import sys
import json

from testwizard.commands_core import CommandBase
from .WaitForPatternResult import WaitForPatternResult

class WaitForPatternCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "WaitForPattern")
    
    def execute(self, filename, minSimilarity, timeout, mode, x, y, width, height):
        if(filename == None):
            raise Exception("filename is required")
        if(minSimilarity == None):
            raise Exception("minSimilarity is required")
        if(timeout == None):
            raise Exception("timeout is required")
        if(mode == None):
            raise Exception("mode is required")
        if(x == None):
            raise Exception("x is required")
        if(y == None):
            raise Exception("y is required")
        if(width == None):
            raise Exception("width is required")
        if(height == None):
            raise Exception("height is required")

        requestObj = [filename, minSimilarity, timeout, mode, x, y, width, height]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return WaitForPatternResult(response.read(), "WaitForPattern was successful", "WaitForPattern failed")