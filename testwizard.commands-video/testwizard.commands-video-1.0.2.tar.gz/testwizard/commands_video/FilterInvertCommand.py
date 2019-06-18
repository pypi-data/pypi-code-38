import sys
import json

from testwizard.commands_core import CommandBase
from .FilterResult import FilterResult

class FilterInvertCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "FilterInvert")
    
    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return FilterResult(response.read(), "FilterInvert was successful", "FilterInvert failed")