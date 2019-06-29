from __future__ import absolute_import, division, print_function

import falcon
import json
import template
from hcli import api
from hcli import home
from hcli import document
from hcli import command
from hcli import option
from hcli import execution
from hcli import finalexecution
from hcli import parameter
import config

class HCLI:
    connector = None
    
    def __init__(self, plugin_path=None):

        # We load the HCLI template in memory to reduce disk io
        config.set_plugin_path(plugin_path)
        config.parse_template(template.Template())

        # We setup the HCLI Connector
        server = falcon.API()
        server.add_route(home.HomeController.route, api.HomeApi())
        server.add_route(document.DocumentController.route, api.DocumentApi())
        server.add_route(command.CommandController.route, api.CommandApi())
        server.add_route(option.OptionController.route, api.OptionApi())
        server.add_route(execution.ExecutionController.route, api.ExecutionApi())
        server.add_route(finalexecution.FinalGetExecutionController.route, api.FinalExecutionApi())
        server.add_route(finalexecution.FinalPostExecutionController.route, api.FinalExecutionApi())
        server.add_route(parameter.ParameterController.route, api.ParameterApi())

        self.connector = server
