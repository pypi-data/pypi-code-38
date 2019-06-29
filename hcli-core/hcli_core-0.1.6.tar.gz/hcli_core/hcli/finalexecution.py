from __future__ import absolute_import, division, print_function

import json
import sys
import config
from haliot import hal
from hcli import semantic
from hcli import profile
from hcli import document
from hcli import home

class FinalGetExecutionLink:
    href = "/hcli/cli/exec/getexecute"
    profile = profile.ProfileLink().href + semantic.hcli_execution_type
    
    def __init__(self, command=None):
        if command != None:
            self.href = self.href + "?command=" + command

class FinalGetExecutionController:
    route = "/hcli/cli/exec/getexecute"
    resource = None

    def __init__(self, command=None):
        if command != None:
            commands = command.split()
            self.resource = config.cli.CLI(commands, None)
            
    def serialize(self):
        return self.resource.execute()

class FinalPostExecutionLink:
    href = "/hcli/cli/exec/postexecute"
    profile = profile.ProfileLink().href + semantic.hcli_execution_type

    def __init__(self, command=None):
        if command != None:
            self.href = self.href + "?command=" + command

class FinalPostExecutionController:
    route = "/hcli/cli/exec/postexecute"
    resource = None

    def __init__(self, command=None, inputstream=None):
        if command != None:
            commands = command.split()
            self.resource = config.cli.CLI(commands, inputstream)

    def serialize(self):
        return self.resource.execute()    
