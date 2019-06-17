import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class SwipeArcCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.SwipeArc")

    def execute(self, centerX, centerY, radius, startDegree, degrees, steps):
        if(centerX==None):
            raise Exception("centerX is required")
        if(centerY==None):
            raise Exception("centerY is required")
        if(radius==None):
            raise Exception("radius is required")
        if(startDegree==None):
            raise Exception("startDegree is required")
        if(degrees==None):
            raise Exception("degrees is required")
        if(steps==None):
            raise Exception("steps is required")   

        requestObj = [centerX, centerY, radius, startDegree, degrees, steps]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "SwipeArc was successful", "SwipeArc failed")