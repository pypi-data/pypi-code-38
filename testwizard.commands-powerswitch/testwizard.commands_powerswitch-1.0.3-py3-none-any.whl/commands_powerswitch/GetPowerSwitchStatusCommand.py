import sys
import json

from testwizard.commands_core import CommandBase
from .GetPowerSwitchStatusResult import GetPowerSwitchStatusResult

class GetPowerSwitchStatusCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "GetPowerSwitchStatus")

    def execute(self):
        requestObj = []
        requestObj = json.dumps(requestObj)

        response = self.robot.post(self.url, requestObj, "Could not execute command")

        return GetPowerSwitchStatusResult(response.read(), "GetPowerSwitchStatus was successful", "GetPowerSwitchStatus failed")