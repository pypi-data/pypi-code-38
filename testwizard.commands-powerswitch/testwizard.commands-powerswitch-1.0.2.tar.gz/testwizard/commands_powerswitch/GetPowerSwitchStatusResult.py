import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class GetPowerSwitchStatusResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if "status" in jsonObj else False, successMessage, failMessage)

        if("status" in jsonObj):
            self.status = jsonObj["status"]