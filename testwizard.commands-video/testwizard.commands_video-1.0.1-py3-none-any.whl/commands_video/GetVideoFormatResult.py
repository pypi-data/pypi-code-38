import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class GetVideoFormatResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        if("format" in jsonObj):
            self.videoFormat = jsonObj["format"]

        ResultBase.__init__(self, True if jsonObj["format"] else False, successMessage, failMessage)