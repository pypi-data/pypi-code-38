import json
import urllib
import config
import re

class Template:
    hcliTemplateVersion = "1.0"
    executable = []
    cli = []

    """ We load the template.json and populate available commands, executables directives and the template version """
    def __init__(self):
        
        try:
            with open(config.plugin_path + "/template.json", "r") as read_file:
                data = json.load(read_file)	

            self.hcliTemplateVersion = data['hcliTemplateVersion']
            self.executable = data['executable']
            self.cli = data['cli']
        except:
            None

    """ We attempt to retrieves a specific command, identified by href, for a given command (uid) """
    def findCommandForId(self, uid, href):
        for index, i in enumerate(self.cli):
            arg = self.cli[index]
            if arg['id'] == uid:
                commands = arg['command']

                for index, j in enumerate(commands):
                    command = commands[index]
                    if command['href'] == href:
                        return command

        return None

    """ We attempt to find the command identified by uid """
    def findById(self, uid):
        for index, i in enumerate(self.cli):
            arg = self.cli[index]
            if arg['id'] == uid:
                return arg
 
        return None

    def findRoot(self):
        return self.cli[0]

    def findCommandsForId(self, uid):
        for index, i in enumerate(self.cli):
            arg = self.cli[index]
            if arg['id'] == uid:
                if 'command' in arg:
                    return arg['command']
        
        return None

    def findOptionsForId(self, uid):
        for index, i in enumerate(self.cli):
            arg = self.cli[index]
            if arg['id'] == uid:
                if 'option' in arg:
                    return arg['option']

        return None

    def findParameterForId(self, uid):
        for index, i in enumerate(self.cli):
            arg = self.cli[index]
            if arg['id'] == uid:
                if 'parameter' in arg:
                    return arg['parameter']

        return None

    """ We attempt to retrieves a specific option, identified by href, for a given command (uid) """
    def findOptionForId(self, uid, href):
        for index, i in enumerate(self.cli):
            arg = self.cli[index]
            if arg['id'] == uid:
                options = arg['option']

                for index, j in enumerate(options):
                    option = options[index]
                    if option['href'] == href:
                        return option

    """ We attempt to retrieves a specific executable, identified by a command line sequence"""
    def findExecutable(self, command):
        for index, i in enumerate(self.executable):
            ex = self.executable[index]
            command = urllib.parse.unquote(command)
            command = re.sub(r'\'.*\'', '{p}', command)
            command = re.sub(r'\".*\"', '{p}', command)
            if(ex['command'] == command):
                return ex

        return None
