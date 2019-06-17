import sys
import json

from testwizard.commands_core import CommandBase
from .ScreenshotResult import ScreenshotResult

class ScreenshotBMP(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.ScreenShotBMP")
    
    def execute(self, filename):
        if(filename==None):
            raise Exception("filename is required")
        requestObj = [filename]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        return ScreenshotResult(response.read(),"ScreenshotBMP was successful", "ScreenshotBMP failed")   