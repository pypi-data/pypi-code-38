from hcli import home
from hcli import document
from hcli import command as hcommand
from hcli import option
from hcli import execution
from hcli import finalexecution
from hcli import parameter

class HomeApi:
    def on_get(self, req, resp):
        resp.content_type = "application/hal+json"
        resp.body = home.HomeController().serialize()

class DocumentApi:
    def on_get(self, req, resp, uid):
        command = req.params['command']

        resp.content_type = "application/hal+json"
        resp.body = document.DocumentController(uid, command).serialize()

class CommandApi:
    def on_get(self, req, resp, uid):
        command = req.params['command']
        href = req.params['href']

        resp.content_type = "application/hal+json"
        resp.body = hcommand.CommandController(uid, command, href).serialize()

class OptionApi:
    def on_get(self, req, resp, uid):
        command = req.params['command']
        href = req.params['href']

        resp.content_type = "application/hal+json"
        resp.body = option.OptionController(uid, command, href).serialize()

class ParameterApi:
    def on_get(self, req, resp, uid):
        command = req.params['command']
        href = req.params['href']

        resp.content_type = "application/hal+json"
        resp.body = parameter.ParameterController(uid, command, href).serialize()

class ExecutionApi:
    def on_get(self, req, resp, uid):
        command = req.params['command']

        resp.content_type = "application/hal+json"
        resp.body = execution.ExecutionController(uid, command).serialize()

class FinalExecutionApi:
    def on_get(self, req, resp):
        command = req.params['command']

        resp.content_type = "application/octet-stream"
        resp.stream = finalexecution.FinalGetExecutionController(command).serialize()

    def on_post(self, req, resp):
        command = req.params['command']

        resp.content_type = "application/octet-stream"
        resp.stream = finalexecution.FinalPostExecutionController(command, req.stream).serialize()        
