import config
import json
import urllib
from haliot import hal
from hcli import semantic
from hcli import profile
from hcli import document
from hcli import home

class Command:
    hcli_version = None
    name = None
    description = None

    def __init__(self, command=None):
        if command != None:
            hcli_version = "1.0"
            self.name = command['name']
            self.description = command['description']

class CommandLink:
    href = "/hcli/cli/__cdef"
    profile = profile.ProfileLink().href + semantic.hcli_command_type
    
    def __init__(self, uid=None, command=None, href=None):
        if uid != None and command != None and href != None:
            self.href = self.href + "/" + uid + "?command=" + urllib.parse.quote(command) + "&href=" + href

class CommandController:
    route = "/hcli/cli/__cdef/{uid}"
    resource = None

    def __init__(self, uid=None, command=None, href=None):
        if uid != None and command != None and href != None:
            t = config.template
            com = t.findCommandForId(uid, href)
            name = com['name']
           
            self.resource = hal.Resource(Command(com))
            selflink = hal.Link(href=CommandLink(uid, command, href).href)
            profilelink = hal.Link(href=CommandLink().profile)
            clilink = hal.Link(href=document.DocumentLink(href, command).href,
                               name=name,
                               profile=document.DocumentLink().profile)
            homelink = hal.Link(href=home.HomeLink().href)

            self.resource.addLink("self", selflink)
            self.resource.addLink("profile", profilelink)
            self.resource.addLink("cli", clilink)
            self.resource.addLink("home", homelink)

    def serialize(self):
        return self.resource.serialize()
