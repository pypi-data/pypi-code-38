import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class SwipeCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.Swipe")
    
    def execute(self, startX, startY, endX, endY, duration):
        if(startX==None):
            raise Exception("startX is required")
        if(startY==None):
            raise Exception("startY is required")
        if(endX==None):
            raise Exception("endX is required")
        if(endY==None):
            raise Exception("endY is required")
        if(duration==None):
            raise Exception("duration is required")

        requestObj = [startX, startY, endX, endY, duration]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "Swipe was successful", "Swipe failed")