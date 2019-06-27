"""
Client creation action.
~~~~~~~~~~~~~~~~~~~~~~~
"""

from .action import Action
from .action import ActionExecutionException
from .action import InvalidActionConfigurationException
from .utils import get_user_roles
from .utils import InvalidUserResponse
from .utils import process_user_roles

import requests
import urllib


class CreateClientAction(Action):

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

        super(CreateClientAction, self).__init__(name, *args, **kwargs)
        self.action_config_json = action_config_json

        if 'realmName' not in action_config_json:
            raise InvalidActionConfigurationException('Configuration "{0}" missing property "realmName"'.format(name))

        self.realm_name = action_config_json['realmName']

        if 'client' not in action_config_json:
            raise InvalidActionConfigurationException('Configuration "{0}" missing property "client"'.format(name))

        self.client_data = action_config_json['client']
        self.client_id = self.client_data.get('clientId', None)

        if not self.client_id:
            raise InvalidActionConfigurationException('Client configuration for "{0}" missing property "clientId"'.format(name))

    def execute(self, keycloak_client):
        """
        Execute this action. In this case, attempt to create a client.
        :param keycloak_client: The client to use when interacting with Keycloak
        """

        # Process the client data.
        print('==== Creating client "{0}" in realm "{1}"...'.format(self.client_id, self.realm_name))
        existing_client_data = self.get_client_by_client_id(self.realm_name, self.client_id, keycloak_client)

        if not existing_client_data:
            print('==== Client "{0}" does not exist, creating...'.format(self.client_id))
            client_creation_path = '/admin/realms/{0}/clients'.format(urllib.parse.quote(self.realm_name))
            create_response = keycloak_client.post(client_creation_path, json=self.client_data)
            if create_response.status_code == requests.codes.created:
                print('==== Client "{0}" created.'.format(self.client_id))
                existing_client_data = self.get_client_by_client_id(self.realm_name, self.client_id, keycloak_client)
                client_uuid = existing_client_data['id']
            else:
                raise ActionExecutionException('Unexpected response for client creation request ({0})'.format(create_response.status_code))
        else:
            print('==== Client "{0}" exists, updating...'.format(self.client_id))
            client_uuid = existing_client_data['id']
            client_update_path = '/admin/realms/{0}/clients/{1}'.format(
                    urllib.parse.quote(self.realm_name),
                    urllib.parse.quote(client_uuid)
            )
            update_response = keycloak_client.put(client_update_path, json=self.client_data)
            if update_response.status_code == requests.codes.no_content:
                print('==== Client "{0}" updated.'.format(self.client_id))
            else:
                raise ActionExecutionException('Unexpected response for client update request ({0})'.format(update_response.status_code))

            # Now update the secret.
            if 'secret' in self.client_data:
                print('==== NOT updating client "{0}" secret, as it is currently broken...'.format(self.client_id))

            # NOTE: the following code is disabled because it requires a custom keycloak extension, which is not currently working
            if False and 'secret' in self.client_data:
                print('==== Updating client "{0}" secret...'.format(self.client_id))
                client_secret_update_path = '/realms/{0}/clients-custom/{1}/client-secret'.format(
                        urllib.parse.quote(self.realm_name),
                        urllib.parse.quote(client_uuid)
                )
                client_secret_update_response = keycloak_client.put(
                        client_secret_update_path, json={'secret': self.client_data['secret']}
                )
                if client_secret_update_response.status_code == requests.codes.no_content:
                    print('==== Client "{0}" secret updated.'.format(self.client_id))
                else:
                    raise ActionExecutionException('Unexpected response for client secret update request ({0})'.format(
                            client_secret_update_response.status_code
                    ))

        # We always need to process mappers, as Keycloak adds default mappers on client creation calls.
        self.update_protocol_mappers(existing_client_data, keycloak_client)

        # Process the service account roles.
        self.process_service_account_roles(client_uuid, self.action_config_json.get('roles', []), keycloak_client)

    def update_protocol_mappers(self, existing_client_data, keycloak_client):
        """
        Update the protocol mappers for the client.
        :param existing_client_data: The existing client data
        :param keycloak_client: The client to use when interacting with Keycloak
        """

        print('==== Processing client "{0}" protocol mappers...'.format(self.client_id))
        client_uuid = existing_client_data['id']
        existing_mappers = existing_client_data['protocolMappers']
        new_mappers = self.client_data['protocolMappers']

        # Mapper names are unique, so we can use that field to see what needs to be updated, created, or deleted.
        existing_mappers_by_name = self.mapper_list_to_map_by_name(existing_mappers)
        new_mappers_by_name = self.mapper_list_to_map_by_name(new_mappers)

        # See what needs to be created or updated.
        for name, config in new_mappers_by_name.items():
            if name in existing_mappers_by_name:
                self.update_protocol_mapper(client_uuid, existing_mappers_by_name[name]['id'], config, keycloak_client)
            else:
                self.create_protocol_mapper(client_uuid, config, keycloak_client)

        # See what needs to be deleted.
        for name, config in existing_mappers_by_name.items():
            if name not in new_mappers_by_name:
                self.delete_protocol_mapper(client_uuid, existing_mappers_by_name[name]['id'], name, keycloak_client)

        print('==== Processed client "{0}" protocol mappers.'.format(self.client_id))

    @staticmethod
    def mapper_list_to_map_by_name(mapper_list):
        """
        Convert a list of protocol mappers to a map of mappers by keyed by name.
        :param mapper_list: The list to convert
        :return: The resulting map
        """

        by_name = {}
        for mapper in mapper_list:
            by_name[mapper['name']] = mapper
        return by_name

    def update_protocol_mapper(self, client_uuid, mapper_id, mapper_config, keycloak_client):
        """
        Update a protocol mapper.
        :param client_uuid: The UUID of the client
        :param mapper_id: the UUID of the mapper
        :param mapper_config: The mapper config to use in the update request
        :param keycloak_client: The client to use when interacting with Keycloak
        """

        print('==== Updating client "{0}" protocol mapper "{1}".'.format(self.client_id, mapper_config['name']))
        path = '/admin/realms/{0}/clients/{1}/protocol-mappers/models/{2}'.format(
                urllib.parse.quote(self.realm_name),
                urllib.parse.quote(client_uuid),
                urllib.parse.quote(mapper_id)
        )

        mapper_config['id'] = mapper_id
        update_response = keycloak_client.put(path, json=mapper_config)
        if update_response.status_code != requests.codes.no_content:
            raise ActionExecutionException('Unexpected response for client protocol mapper update request ({0})'.format(update_response.status_code))

    def create_protocol_mapper(self, client_uuid, mapper_config, keycloak_client):
        """
        Create a protocol mapper.
        :param client_uuid: The UUID of the client
        :param mapper_config: The mapper config to use in the create request
        :param keycloak_client: The client to use when interacting with Keycloak.
        :return:
        """

        print('==== Creating client "{0}" protocol mapper "{1}".'.format(self.client_id, mapper_config['name']))
        path = '/admin/realms/{0}/clients/{1}/protocol-mappers/models'.format(
                urllib.parse.quote(self.realm_name),
                urllib.parse.quote(client_uuid)
        )

        create_response = keycloak_client.post(path, json=mapper_config)
        if create_response.status_code != requests.codes.created:
            raise ActionExecutionException('Unexpected response for client protocol mapper create request ({0})'.format(create_response.status_code))

    def delete_protocol_mapper(self, client_uuid, mapper_id, mapper_name, keycloak_client):
        """
        Delete a protocol mapper.
        :param client_uuid: The UUID of the client
        :param mapper_id: the UUID of the mapper
        :param mapper_name: The name of the mapper
        :param keycloak_client: The client to use when interacting with Keycloak
        """

        print('==== Deleting client "{0}" protocol mapper "{1}".'.format(self.client_id, mapper_name))
        path = '/admin/realms/{0}/clients/{1}/protocol-mappers/models/{2}'.format(
                urllib.parse.quote(self.realm_name),
                urllib.parse.quote(client_uuid),
                urllib.parse.quote(mapper_id)
        )

        delete_response = keycloak_client.delete(path)
        if delete_response.status_code != requests.codes.no_content:
            raise ActionExecutionException('Unexpected response for client protocol mapper delete request ({0})'.format(delete_response.status_code))

    def get_service_account_user(self, client_uuid, keycloak_client):
        """
        Get the service account user for the client.
        :param client_uuid: The client UUID
        :param keycloak_client: The client to use when interacting with Keycloak
        :return: The service account user configuration
        """

        path = '/admin/realms/{0}/clients/{1}/service-account-user'.format(self.realm_name, client_uuid)
        get_response = keycloak_client.get(path)

        if get_response.status_code == requests.codes.ok:
            return get_response.json()

        if get_response.status_code == requests.codes.not_found:
            return None

        raise InvalidUserResponse('Unexpected user get response ({0})'.format(get_response.status_code))

    def process_service_account_roles(self, client_uuid, service_account_roles, keycloak_client):
        """
        Process the service account roles for the client.
        :param client_uuid: The client UUID
        :param service_account_roles: The roles to assign to the service account
        :param keycloak_client: The client to use when interacting with Keycloak
        """

        print('==== Processing client "{0}" service account roles...'.format(self.client_id))
        user_config = self.get_service_account_user(client_uuid, keycloak_client)
        if not user_config and len(service_account_roles) > 0:
            raise ActionExecutionException('No service account user found for client "{0}"'.format(self.client_id))

        user_id = user_config['id']
        existing_roles = get_user_roles(self.realm_name, user_id, keycloak_client)
        process_user_roles(self.realm_name, user_id, existing_roles, service_account_roles, keycloak_client)
        print('==== Processed client "{0}" service account roles.'.format(self.client_id))
