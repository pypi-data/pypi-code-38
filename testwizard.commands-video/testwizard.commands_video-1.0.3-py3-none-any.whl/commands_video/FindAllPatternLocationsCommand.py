import sys
import json

from testwizard.commands_core import CommandBase
from .FindAllPatternLocationsResult import FindAllPatternLocationsResult

class FindAllPatternLocationsCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "FindAllPatternLocations")
    
    def execute(self, filename, mode, similarity):
        if(filename==None):
            raise Exception("filename is required")
        if(mode==None):
            raise Exception("mode is required")
        if(similarity==None):
            raise Exception("similarity is required")

        requestObj = [filename, mode, similarity]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return FindAllPatternLocationsResult(response.read(), "FindAllPatternLocations was successful", "FindAllPatternLocations failed")