import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class ZoomCoordinatesCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.ZoomCoordinates")

    def execute(self, x, y, length):
        if(x==None):
            raise Exception("x is required")
        if(y==None):
            raise Exception("y is required")
        if(length==None):
            raise Exception("length is required")

        requestObj = [x, y, length]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "ZoomCoordinates was successful", "ZoomCoordinates failed")