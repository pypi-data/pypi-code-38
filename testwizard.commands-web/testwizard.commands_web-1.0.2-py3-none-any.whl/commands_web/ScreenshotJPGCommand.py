import sys
import json

from testwizard.commands_core import CommandBase
from .ScreenshotResult import ScreenshotResult

class ScreenshotJPGCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.ScreenShotJPG")

    def execute(self, filename, quality):
        if(filename==None):
            raise Exception("filename is required")
        if(quality==None):
            raise Exception("quality is required")

        requestObj = [filename, quality]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return ScreenshotResult(response.read(),"ScreenshotJPG was successful", "ScreenshotJPG failed")