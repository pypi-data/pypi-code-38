import os
import yaml


class RESTConfig:
    def __init__(self, file):
        with open(file) as f:
            config = {x[0].upper(): x[1] for x in yaml.safe_load(f).items()}
        self.ENVIRONMENT = (os.environ.get('ENVIRONMENT') or os.environ.get('ENV') or 'DEFAULT').upper()
        self.__config = config.get(self.ENVIRONMENT) or {}
        self.__default = config.get('DEFAULT') or {}

        for param in self.__annotations__:
            value = os.environ.get(param.upper()) or self.__config.get(param) or self.__default.get(param)
            self.__dict__[param] = value
