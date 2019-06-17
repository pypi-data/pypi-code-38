import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkResult import OkResult

class CaptureReferenceBitmapCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "CaptureReferenceBitmap")

    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkResult(response.read(), "CaptureReferenceBitmap was successful", "CaptureReferenceBitmap failed")   