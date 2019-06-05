import sys

if sys.version_info > (3, 0):
    import configparser as ConfigParser
else:
    import ConfigParser
import os.path

class IniLoader():
    def getConfig(self, environment):
        configLocations = ['/etc/strongr/config.ini', os.path.expanduser('~/.strongr/config.ini'), 'config.ini']
        output = {}

        return output # return nothing for now, below code does not work anymore

        for configLocation in configLocations:
            if os.path.isfile(configLocation):
                config = ConfigParser.ConfigParser()
                config.read(configLocation)
                for key in config.defaults():
                    output[key] = config.defaults()[key]
                for key in config.options(environment):
                    output[key] = config.get(environment, key)

        return output

