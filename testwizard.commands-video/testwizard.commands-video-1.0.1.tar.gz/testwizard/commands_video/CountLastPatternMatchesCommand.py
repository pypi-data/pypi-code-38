import sys
import json

from testwizard.commands_core import CommandBase
from .CountLastPatternMatchesResult import CountLastPatternMatchesResult

class CountLastPatternMatchesCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "CountLastPatternMatches")
    
    def execute(self, similarity):
        if(similarity==None):
            raise Exception("similarity is required")

        requestObj = [similarity]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return CountLastPatternMatchesResult(response.read(), "CountLastPatternMatches was successful", "CountLastPatternMatches failed")   