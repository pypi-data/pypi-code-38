import config
from haliot import hal
from hcli import document

class Home(object):
    None

class HomeLink:
    href = None

    def __init__(self):
        self.href = "/"

class HomeController:
    route = "/"
    resource = None

    def __init__(self):

        t = config.template

        if t and t.cli and t.hcliTemplateVersion and t.hcliTemplateVersion == "1.0":
            root = t.findRoot()
            uid = root['id']
            command = root['name']

            self.resource = hal.Resource(Home())
            selflink = hal.Link(href=HomeLink().href)
            clilink = hal.Link(href=document.DocumentLink(uid, command).href,
                               profile=document.DocumentLink().profile)

            self.resource.addLink("self", selflink)
            self.resource.addLink("cli", clilink)

    def serialize(self):
        return self.resource.serialize()
