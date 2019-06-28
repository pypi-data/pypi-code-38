import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class MultiAction_DragAndDrop(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.MultiAction_DragAndDrop")

    def execute(self, sourceSelector, targetSelector):
        if(sourceSelector==None):
            raise Exception("sourceSelector is required")
        if(targetSelector==None):
            raise Exception("targetSelector is required")

        requestObj = [sourceSelector, targetSelector]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"MultiAction_DragAndDrop was successful", "MultiAction_DragAndDrop failed")