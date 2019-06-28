import sys
import json

from testwizard.commands_core import CommandBase
from .TextOCRResult import TextOCRResult

class TextOCRCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "TextOCR")

    def execute(self, characterSet, dictionary):
        if(characterSet==None):
            raise Exception("x is required")
        if(dictionary==None):
            raise Exception("y is required")

        requestObj = [characterSet, dictionary]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return TextOCRResult(response.read(), "TextOCR was successful", "TextOCR failed")