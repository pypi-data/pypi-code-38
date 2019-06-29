import config
import json
import urllib
from haliot import hal
from hcli import semantic
from hcli import profile
from hcli import document
from hcli import home
from hcli import finalexecution

class Execution:
    hcli_version = None
    command = None
    http = None

    def __init__(self, executable=None):
        if executable != None:
            hcli_version = "1.0"
            self.command = executable['command']
            self.http = executable['http']

class ExecutionLink:
    href = "/hcli/cli/__edef"
    profile = profile.ProfileLink().href + semantic.hcli_execution_type
    
    def __init__(self, uid=None, command=None):
        if uid != None and command != None:
            self.href = self.href + "/" + uid + "?command=" + urllib.parse.quote(command)

class ExecutionController:
    route = "/hcli/cli/__edef/{uid}"
    resource = None

    def __init__(self, uid=None, command=None):
        if uid != None and command != None:
            t = config.template
            arg = t.findById(uid);
            ex = t.findExecutable(command)
            http = ex['http']
           
            self.resource = hal.Resource(Execution(ex))
            selflink = hal.Link(href=ExecutionLink(uid, command).href)
            profilelink = hal.Link(href=ExecutionLink().profile)
            homelink = hal.Link(href=home.HomeLink().href)

            if http == 'get':
                finallink = hal.Link(href=finalexecution.FinalGetExecutionLink(command).href)
                self.resource.addLink("cli", finallink)
            
            if http == 'post':
                finallink = hal.Link(href=finalexecution.FinalPostExecutionLink(command).href)
                self.resource.addLink("cli", finallink)

            self.resource.addLink("self", selflink)
            self.resource.addLink("profile", profilelink)
            self.resource.addLink("home", homelink)

    def serialize(self):
        return self.resource.serialize()
