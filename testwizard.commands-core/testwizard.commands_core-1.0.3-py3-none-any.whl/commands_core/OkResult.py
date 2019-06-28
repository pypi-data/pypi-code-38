import json
import sys

from .ResultBase import ResultBase

class OkResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if jsonObj["ok"] else False, successMessage, failMessage)