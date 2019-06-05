import os.path
import yaml

class YamlLoader():
    def getConfig(self, environment):
        configLocations = ['/etc/strongr/config.yml', os.path.expanduser('~/.strongr/config.yml'), 'config.yml']
        output = {}

        envs = ['defaults', environment]

        for configLocation in configLocations:
            if os.path.isfile(configLocation):
                with open(configLocation) as yamlFile:
                    data = yaml.load(yamlFile)
                for env in envs:
                    if env in data:
                        for key in data[env]:
                            output[key] = data[env][key]
        return output
