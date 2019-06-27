"""
User creation action.
~~~~~~~~~~~~~~~~~~~~~
"""

from .action import Action
from .action import ActionExecutionException
from .action import InvalidActionConfigurationException
from .utils import get_user_by_email
from .utils import get_user_roles
from .utils import process_user_roles

import requests
import urllib


class CreateUserAction(Action):

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

        super(CreateUserAction, self).__init__(name, *args, **kwargs)
        self.action_config_json = action_config_json

        if 'realmName' not in action_config_json:
            raise InvalidActionConfigurationException('Configuration "{0}" missing property "realmName"'.format(name))

        self.realm_name = action_config_json['realmName']

        if 'user' not in action_config_json:
            raise InvalidActionConfigurationException('Configuration "{0}" missing property "user"'.format(name))

        self.user_data = action_config_json['user']
        self.email = self.user_data.get('email', None)

        if not self.email:
            raise InvalidActionConfigurationException('User configuration for "{0}" missing property "email"'.format(name))

        # Username is the same as the email.
        self.user_data['username'] = self.email

        self.password = action_config_json.get('password', None)
        self.roles = action_config_json.get('roles', [])

    def execute(self, keycloak_client):
        """
        Execute this action. In this case, attempt to create a user.
        :param keycloak_client: The client to use when interacting with Keycloak
        """

        # Process the user data.
        print('==== Creating user "{0}" in realm "{1}"...'.format(self.email, self.realm_name))
        existing_user_data = get_user_by_email(self.realm_name, self.email, keycloak_client)

        if not existing_user_data:
            print('==== User "{0}" does not exist, creating...'.format(self.email))
            user_creation_path = '/admin/realms/{0}/users'.format(urllib.parse.quote(self.realm_name))
            create_response = keycloak_client.post(user_creation_path, json=self.user_data)
            if create_response.status_code == requests.codes.created:
                print('==== User "{0}" created.'.format(self.email))
                existing_user_data = get_user_by_email(self.realm_name, self.email, keycloak_client)
            else:
                raise ActionExecutionException('Unexpected response for user creation request ({0})'.format(create_response.status_code))
        else:
            print('==== User "{0}" exists, updating...'.format(self.email))
            user_update_path = '/admin/realms/{0}/users/{1}'.format(
                    urllib.parse.quote(self.realm_name),
                    urllib.parse.quote(existing_user_data['id'])
            )
            update_response = keycloak_client.put(user_update_path, json=self.user_data)
            if update_response.status_code == requests.codes.no_content:
                print('==== User "{0}" updated.'.format(self.email))
            else:
                raise ActionExecutionException('Unexpected response for user update request ({0})'.format(update_response.status_code))

        user_uuid = existing_user_data['id']

        print('==== Processing user "{0}" roles...'.format(self.email))
        existing_roles = get_user_roles(self.realm_name, user_uuid, keycloak_client)
        process_user_roles(self.realm_name, user_uuid, existing_roles, self.roles, keycloak_client)
        print('==== Processed user "{0}" roles.'.format(self.email))

        if self.password:
            print('==== Updating password for user "{0}"...'.format(self.email, self.realm_name))
            password_payload = {
                'value': self.password,
                'type': 'password',
                'temporary': False
            }
            password_path = '/admin/realms/{0}/users/{1}/reset-password'.format(self.realm_name, user_uuid)
            password_response = keycloak_client.put(password_path, json=password_payload)
            if password_response.status_code == requests.codes.no_content:
                print('==== User "{0}" password updated.'.format(self.email))
            else:
                raise ActionExecutionException('Unexpected response for user password request ({0})'.format(password_response.status_code))
