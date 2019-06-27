"""
Client deletion action.
~~~~~~~~~~~~~~~~~~~~~~~
"""

from .action import Action
from .action import ActionExecutionException
from .action import InvalidActionConfigurationException

import requests
import urllib


class DeleteClientAction(Action):

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

        super(DeleteClientAction, self).__init__(name, *args, **kwargs)
        self.action_config_json = action_config_json

        if 'realmName' not in action_config_json:
            raise InvalidActionConfigurationException('Configuration "{0}" missing property "realmName"'.format(name))

        self.realm_name = action_config_json['realmName']

        if 'clients' not in action_config_json:
            raise InvalidActionConfigurationException('Configuration "{0}" missing property "clients"'.format(name))

        self.clients_data = action_config_json['clients']

    def execute(self, keycloak_client):
        """
        Execute this action. In this case, attempt to delete a client.
        :param keycloak_client: The client to use when interacting with Keycloak
        """

        # Process the client data.
        for client in self.clients_data:
            print('==== Deleting client "{0}" in realm "{1}"...'.format(client, self.realm_name))
            existing_client_data = self.get_client_by_client_id(self.realm_name, client, keycloak_client)
            if not existing_client_data:
                print('==== Client "{0}" does not exist, skip...'.format(client))
            else:
                print('==== Client "{0}" exists, deleting...'.format(client))
                client_uuid = existing_client_data['id']
                client_delete_path = '/admin/realms/{0}/clients/{1}'.format(
                        urllib.parse.quote(self.realm_name),
                        urllib.parse.quote(client_uuid)
                )
                response = keycloak_client.delete(client_delete_path)
                if response.status_code == requests.codes.no_content:
                    print('==== Client "{0}" deleted.'.format(client))
                else:
                    raise ActionExecutionException('Unexpected response for client delete request ({0})'.format(response.status_code))
