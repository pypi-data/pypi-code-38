import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class GetVideoResolutionResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        self.width = jsonObj["width"]
        self.height = jsonObj["height"]
        ResultBase.__init__(self, False if self.width==-1 or self.height==-1 else True, successMessage, failMessage)