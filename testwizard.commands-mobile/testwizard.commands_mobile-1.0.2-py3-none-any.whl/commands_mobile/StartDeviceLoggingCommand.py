import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class StartDeviceLoggingCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.StartDeviceLogging")

    def execute(self, filename, username=None, password=None):
        if (filename == None):
            raise Exception("filename is required")

        requestObj = [filename, username, password]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SimpleResult(response.read(), "StartDeviceLogging was successful", "StartDeviceLogging failed")
