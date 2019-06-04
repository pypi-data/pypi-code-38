import os
import re
import yaml

from pkg_resources import resource_string


class Configuration:
    path_matcher = re.compile(r'\$\{([^}^{]+)\}')

    def __init__(self, package=None, yaml_file=None):
        yaml.add_implicit_resolver('!path', self.path_matcher, None, yaml.SafeLoader)
        yaml.add_constructor('!path', self._path_constructor, yaml.SafeLoader)
        if yaml_file is not None:
            yml = resource_string(package, yaml_file)
        else:
            yml = resource_string(__name__, 'config.yaml')
        self.cfg = yaml.safe_load(yml)

    def config(self):
        return self.cfg

    def _path_constructor(self, loader, node):
        value = node.value
        match = self.path_matcher.match(value)
        env_var = match.group()[2:-1]
        return os.environ.get(env_var)

    def get_logging_config(self):
        return self.cfg['logging']
