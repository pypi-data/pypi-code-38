import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult

class AddCapabilityCommand(CommandBase):
    def __init__(self, session, testObjectName):
        CommandBase.__init__(self, session, testObjectName, "Mobile.AddCapability")
    
    def execute(self, name, value):
        
        if(name == None):
            raise Exception("name is required")
        if(value == None):
            raise Exception("value is required")    
        requestObj = json.dumps([name, value])

        response = self.robot.post(self.url, requestObj, "Could not execute command")
        
        return SimpleResult(response.read(), "AddCapability was successful", "AddCapability failed")   