"""
Role creation action.
~~~~~~~~~~~~~~~~~~~~~~~
"""

from .action import Action
from .action import ActionExecutionException
from .action import InvalidActionConfigurationException
from .utils import get_role_by_name

import requests
import urllib


class CreateRoleAction(Action):

    @staticmethod
    def valid_deploy_env(deploy_env):
        """
        Returns True if the provided deployment environment is valid for this action, False otherwise
        :param deploy_env: The target deployment environment.
        :return: True always, as this action is valid for all environments.
        """

        return True

    def __init__(self, name, config_file_dir, action_config_json, *args, **kwargs):
        """
        Constructor.
        :param name: The action name.
        :param config_file_dir: The directory containing the configuration file
        :param action_config_json: The JSON configuration for this action
        """

        super(CreateRoleAction, self).__init__(name, *args, **kwargs)
        self.action_config_json = action_config_json

        if 'realmName' not in action_config_json:
            raise InvalidActionConfigurationException('Configuration "{0}" missing property "realmName"'.format(name))

        self.realm_name = action_config_json['realmName']

        if 'role' not in action_config_json:
            raise InvalidActionConfigurationException('Configuration "{0}" missing property "role"'.format(name))

        self.role_data = action_config_json['role']
        self.role_name = self.role_data.get('name', None)

        if not self.role_name:
            raise InvalidActionConfigurationException('Role configuration for "{0}" missing property "name"'.format(name))

    def execute(self, keycloak_client):
        """
        Execute this action. In this case, attempt to create a role.
        :param keycloak_client: The client to use when interacting with Keycloak
        """

        # Process the role data.
        print('==== Creating role "{0}" in realm "{1}"...'.format(self.role_name, self.realm_name))
        existing_role_data = get_role_by_name(self.realm_name, self.role_name, keycloak_client)

        if not existing_role_data:
            print('==== Role "{0}" does not exist, creating...'.format(self.role_name))
            role_creation_path = '/admin/realms/{0}/roles'.format(urllib.parse.quote(self.realm_name))
            create_response = keycloak_client.post(role_creation_path, json=self.role_data)
            if create_response.status_code == requests.codes.created:
                print('==== Role "{0}" created.'.format(self.role_name))
            else:
                raise ActionExecutionException('Unexpected response for role creation request ({0})'.format(create_response.status_code))
        else:
            print('==== Role "{0}" exists, updating...'.format(self.role_name))
            role_update_path = '/admin/realms/{0}/roles/{1}'.format(
                    urllib.parse.quote(self.realm_name),
                    urllib.parse.quote(self.role_name)
            )
            update_response = keycloak_client.put(role_update_path, json=self.role_data)
            if update_response.status_code == requests.codes.no_content:
                print('==== Role "{0}" updated.'.format(self.role_name))
            else:
                raise ActionExecutionException('Unexpected response for role update request ({0})'.format(update_response.status_code))
