import os.path
import json

class JsonLoader():
    def getConfig(self, environment):
        configLocations = ['/etc/strongr/config.json', os.path.expanduser('~/.strongr/config.json'), 'config.json']
        output = {}

        envs = ['defaults', environment]

        for configLocation in configLocations:
            if os.path.isfile(configLocation):
                with open(configLocation) as jsonFile:
                    data = json.load(jsonFile)
                for env in envs:
                    if env in data:
                        for key in data[env]:
                            output[key] = data[env][key]
        return output
