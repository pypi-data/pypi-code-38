import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult

class MultiAction_DragAndDropToOffset(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Selenium.MultiAction_DragAndDropToOffset")

    def execute(self, sourceSelector, targetXOffset, targetYOffset):
        if(sourceSelector==None):
            raise Exception("sourceSelector is required")
        if(targetXOffset==None):
            raise Exception("targetXOffset is required")
        if(targetYOffset==None):
            raise Exception("targetYOffset is required")

        requestObj = [sourceSelector, targetXOffset, targetYOffset]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(response.read(),"MultiAction_DragAndDropToOffset was successful", "MultiAction_DragAndDropToOffset failed")