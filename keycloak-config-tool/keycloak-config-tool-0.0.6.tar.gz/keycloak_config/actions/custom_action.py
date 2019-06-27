"""
Custom module action.
~~~~~~~~~~~~~~~~~~~~~
"""

from .action import Action
from .action import ActionExecutionException
from .action import InvalidActionConfigurationException

import importlib.machinery
import os


class CustomActionWrapper(Action):

    @staticmethod
    def valid_deploy_env(deploy_env):
        """
        Returns True if the provided deployment environment is valid for this action, False otherwise
        :param deploy_env: The target deployment environment.
        :return: True if this is a valid deploy environment for this action, False otherwise
        """

        return deploy_env == 'local'

    def __init__(self, name, config_file_dir, action_config_json, *args, **kwargs):
        """
        Constructor.
        :param name: The action name.
        :param config_file_dir: The directory containing the configuration file
        :param action_config_json: The JSON configuration for this action
        """

        super(CustomActionWrapper, self).__init__(name, *args, **kwargs)
        self.action_config_json = action_config_json

        if 'file' not in action_config_json:
            raise InvalidActionConfigurationException('Configuration "{0}" missing property "file"'.format(name))

        self.custom_code_file_path = os.path.join(config_file_dir, action_config_json['file'])
        loader = importlib.machinery.SourceFileLoader(name, self.custom_code_file_path)
        handle = loader.load_module(name)
        self.custom_action = handle.CustomAction(name, config_file_dir, action_config_json, InvalidActionConfigurationException)

    def execute(self, keycloak_client):
        """
        Execute this action. In this case, executing a custom action.
        :param keycloak_client: The client to use when interacting with Keycloak.
        """

        print('==== Executing custom action "{0}"...'.format(self.name))
        self.custom_action.execute(keycloak_client, ActionExecutionException)
        print('==== Completed executing custom action "{0}".'.format(self.name))
