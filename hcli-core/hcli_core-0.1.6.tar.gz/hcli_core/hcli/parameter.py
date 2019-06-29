import config
import json
import urllib
from haliot import hal
from hcli import semantic
from hcli import profile
from hcli import document
from hcli import home

class Parameter:
    hcli_version = None

    def __init__(self):
        hcli_version = "1.0"

class ParameterLink:
    href = "/hcli/cli/__pdef"
    profile = profile.ProfileLink().href + semantic.hcli_parameter_type
    
    def __init__(self, uid=None, command=None, href=None):
        if uid != None and command != None and href != None:
            self.href = self.href + "/" + uid + "?command=" + urllib.parse.quote(command) + "&href=" + href

class ParameterController:
    route = "/hcli/cli/__pdef/{uid}"
    resource = None

    def __init__(self, uid=None, command=None, href=None):
        if uid != None and command != None and href != None:
            t = config.template
            arg = t.findById(uid);
            param = t.findParameterForId(uid)
            name = arg['name']
           
            self.resource = hal.Resource(Parameter())
            selflink = hal.Link(href=ParameterLink(uid, command, href).href)
            profilelink = hal.Link(href=ParameterLink().profile)
            clilink = hal.Link(href=document.DocumentLink(uid, urllib.parse.quote(command + " ") + "{hcli_param}", withparam=True).href,
                               name=name,
                               profile=document.DocumentLink().profile,
                               templated=True)
            homelink = hal.Link(href=home.HomeLink().href)

            self.resource.addLink("self", selflink)
            self.resource.addLink("profile", profilelink)
            self.resource.addLink("cli", clilink)
            self.resource.addLink("home", homelink)

    def serialize(self):
        return self.resource.serialize()
