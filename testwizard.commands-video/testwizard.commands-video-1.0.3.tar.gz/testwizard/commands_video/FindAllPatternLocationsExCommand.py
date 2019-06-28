import sys
import json

from testwizard.commands_core import CommandBase
from .FindAllPatternLocationsResult import FindAllPatternLocationsResult

class FindAllPatternLocationsExCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "FindAllPatternLocationsEx")

    def execute(self, filename, mode, similarity, x, y, width, height):
        if(filename==None):
            raise Exception("filename is required")
        if(mode==None):
            raise Exception("mode is required")
        if(similarity==None):
            raise Exception("similarity is required")
        if(x==None):
            raise Exception("x is required")
        if(y==None):
            raise Exception("y is required")
        if(width==None):
            raise Exception("width is required")
        if(height==None):
            raise Exception("height is required")

        requestObj = [filename, mode, similarity, x, y, width, height]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return FindAllPatternLocationsResult(response.read(), "FindAllPatternLocationsEx was successful", "FindAllPatternLocationsEx failed")