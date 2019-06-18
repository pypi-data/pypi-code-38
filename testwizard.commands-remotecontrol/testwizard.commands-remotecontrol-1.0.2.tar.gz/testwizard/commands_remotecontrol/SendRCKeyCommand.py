import sys
import json

from testwizard.commands_core import CommandBase
from .SendRCKeyResult import SendRCKeyResult

class SendRCKeyCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "SendRCKey")

    def execute(self, keyName):
        if(keyName == None):
            raise Exception("keyName is required")

        requestObj = [keyName]
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return SendRCKeyResult(response.read(), "SendRCKey was successful", "SendRCKey failed")