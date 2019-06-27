"""
Deployment Configuration.
~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
import re


class InvalidConfigurationException(Exception):
    pass


class DeployConfig(object):

    def __init__(self, deploy_config_dir, deploy_env, json_loader):
        """
        Constructor.
        :param deploy_config_dir: The base directory for the deployment configuration.
        :param deploy_env: The target deployment environment.
        :param json_loader: An object able to load JSON contents into a Python object.
        """

        self.deploy_config_dir = deploy_config_dir
        self.deploy_env = deploy_env
        self.deploy_src_dir = os.path.join(deploy_config_dir, 'src')
        self.deploy_config_file = os.path.join(self.deploy_src_dir, 'keycloak.json')
        self.deploy_var_dir = os.path.join(deploy_config_dir, 'var')
        self.deploy_keycloak_var_dir = os.path.join(self.deploy_var_dir, 'keycloak')

        if not os.path.isfile(self.deploy_config_file):
            raise InvalidConfigurationException('Configuration file not found: {0}'.format(self.deploy_config_file))

        with open(self.deploy_config_file, 'r') as f:
            self.raw_config = f.read()

        self.variables = self.load_variables()
        self.processed_config = self.process_config_variables()
        self.json_config = json_loader.load_json(self.processed_config)

    def load_variables(self):
        """
        Load the default and environment-specific variable files.
        :return: A dictionary containing all loaded variables.
        """

        default_variables_file = os.path.join(self.deploy_keycloak_var_dir, 'defaults.var')
        default_variables = self.load_variables_file(default_variables_file)

        deploy_env_variables_file = os.path.join(self.deploy_keycloak_var_dir, '{0}.var'.format(self.deploy_env))
        deploy_env_variables = self.load_variables_file(deploy_env_variables_file)

        default_variables.update(deploy_env_variables)
        return default_variables

    @staticmethod
    def load_variables_file(path):
        """
        Load the variable file located at the supplied path.
        :param path: The path of the variable file
        :return: A dictionary containing all loaded variables.
        """

        variables = {}

        if os.path.isfile(path):
            with open(path, 'r') as f:
                for line in f:
                    stripped_line = re.sub(r'#.*$', '', line).strip()

                    if len(line) > 0:
                        tokens = stripped_line.split('=', maxsplit=2)
                        if len(tokens) < 2:
                            raise InvalidConfigurationException('Invalid variable assignment: "{0}"'.format(line))

                        variables[tokens[0].strip()] = tokens[1].strip()

        return variables

    def process_config_variables(self):
        """
        Process the variables contained in the configuration.
        :return: The processed configuration.
        """

        def replacement(matchobj):
            variable = matchobj.group(1).strip()
            if len(variable) == 0:
                raise InvalidConfigurationException('Empty variable declaration in configuration')
            if variable in os.environ:
                return os.environ[variable]
            if variable in self.variables:
                return self.variables[variable]
            raise InvalidConfigurationException('Unknown variable: {0}'.format(variable))

        return re.sub(r'#\{([^}]+)}', replacement, self.raw_config)

    def get_json_config(self):
        return self.json_config

    def get_config_dir(self):
        return self.deploy_src_dir

    def get_processed_config(self):
        return self.processed_config
