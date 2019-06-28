import sys
import json

from testwizard.commands_core import CommandBase
from .CompareResult import CompareResult

class CompareCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Compare")
    
    def execute(self, x, y, width, height, filename, tolerance):
        
        if(x==None):
            raise Exception("x is required")
        if(y==None):
            raise Exception("y is required")
        if(width==None):
            raise Exception("width is required")
        if(height==None):
            raise Exception("height is required")
        if(filename==None):
            raise Exception("filename is required")
        if(tolerance==None):
            raise Exception("tolerance is required")

        requestObj = [x, y, width, height, filename, tolerance]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        
        return CompareResult(response.read(),"compare was successful", "compare failed")   