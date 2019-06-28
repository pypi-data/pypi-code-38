import sys
import json

from testwizard.commands_core import CommandBase
from .FilterResult import FilterResult

class FilterGrayscaleCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "FilterGrayscale")
    
    def execute(self, levels):

        if(levels==None):
            raise Exception("levels is required")
        
        requestObj = [levels]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return FilterResult(response.read(), "FilterGrayscale was successful", "FilterGrayscale failed")   