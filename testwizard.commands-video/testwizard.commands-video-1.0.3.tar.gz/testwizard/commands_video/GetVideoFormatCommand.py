import sys
import json

from testwizard.commands_core import CommandBase
from .GetVideoFormatResult import GetVideoFormatResult

class GetVideoFormatCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "GetVideoFormat")

    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return GetVideoFormatResult(response.read(), "v was successful", "GetVideoFormat failed")