"""
Import realm action.
~~~~~~~~~~~~~~~~~~~~
"""

from .action import Action
from .action import ActionExecutionException
from .action import InvalidActionConfigurationException

import os
import requests
import urllib


class ImportRealmAction(Action):

    @staticmethod
    def valid_deploy_env(deploy_env):
        """
        Returns True if the provided deployment environment is valid for this action, False otherwise
        :param deploy_env: The target deployment environment.
        :return: True if this is a valid deploy environment for this action, False otherwise
        """

        return deploy_env == 'local'

    def __init__(self, name, config_file_dir, action_config_json, json_loader, *args, **kwargs):
        """
        Constructor.
        :param name: The action name.
        :param config_file_dir: The directory containing the configuration file.
        :param action_config_json: The JSON configuration for this action.
        """

        super(ImportRealmAction, self).__init__(name, *args, **kwargs)
        self.action_config_json = action_config_json

        if 'realmFile' not in action_config_json:
            raise InvalidActionConfigurationException('Configuration "{0}" missing property "realmFile"'.format(name))

        self.realm_file_path = os.path.join(config_file_dir, action_config_json['realmFile'])

        if not os.path.isfile(self.realm_file_path):
            raise InvalidActionConfigurationException('Configuration "{0}" realm file not found: {1}'.format(name, self.realm_file_path))

        with open(self.realm_file_path, 'r') as f:
            self.realm_data = json_loader.load_json(f.read())

        self.realm_name = self.realm_data.get('realm', None)

        if not self.realm_name:
            raise InvalidActionConfigurationException('Realm configuration "{0}" missing property "realm"'.format(name))

        self.overwrite = action_config_json.get('overwrite', False)

    def execute(self, keycloak_client):
        """
        Execute this action. In this case, attempt to import a realm.
        :param keycloak_client: The client to use when interacting with Keycloak.
        """

        print('==== Importing realm "{0}"...'.format(self.realm_name))
        realm_path = '/admin/realms/{0}'.format(urllib.parse.quote(self.realm_name))
        import_realm = False

        get_response = keycloak_client.get(realm_path)
        if get_response.status_code == requests.codes.ok:
            if not self.overwrite:
                print('==== Realm "{0}" exists, and overwrite is false.'.format(self.realm_name))
            else:
                delete_response = keycloak_client.delete(realm_path)
                if delete_response.status_code != requests.codes.no_content:
                    raise ActionExecutionException('Unable to delete realm "{0}".'.format(self.realm_name))
                else:
                    print('==== Deleted existing realm "{0}".'.format(self.realm_name))
                    import_realm = True
        elif get_response.status_code == requests.codes.not_found:
            import_realm = True
        else:
            raise ActionExecutionException('Unexpected response for realm existence check ({0})'.format(get_response.status_code))

        if import_realm:
            print('==== Creating realm "{0}"...'.format(self.realm_name))
            post_response = keycloak_client.post('/admin/realms', json=self.realm_data)
            if post_response.status_code == requests.codes.created:
                print('==== Realm "{0}" creation succeeded.'.format(self.realm_name))
            else:
                raise ActionExecutionException('Unexpected response for realm creation ({0})'.format(post_response.status_code))
