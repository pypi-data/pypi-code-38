"""
Actions Engine.
~~~~~~~~~~~~~~~
"""

from .actions.action import InvalidActionConfigurationException
from .actions.create_client import CreateClientAction
from .actions.create_role import CreateRoleAction
from .actions.create_user import CreateUserAction
from .actions.custom_action import CustomActionWrapper
from .actions.delete_client import DeleteClientAction
from .actions.import_realm import ImportRealmAction


class ActionsEngine(object):
    ACTIONS = {
        'importRealm': ImportRealmAction,
        'createClient': CreateClientAction,
        'createUser': CreateUserAction,
        'createRole': CreateRoleAction,
        'deleteClient': DeleteClientAction,
        'custom': CustomActionWrapper
    }

    def __init__(self, deploy_env, config_file_dir, actions_config_json, json_loader):
        self.actions = []
        self.actions_by_name = {}
        self.deploy_env = deploy_env
        self.config_file_dir = config_file_dir
        self.action_config_json = actions_config_json

        self.action_kwargs = {
            'json_loader': json_loader
        }

        for action_config_json in actions_config_json:
            self.process_action_config_json(action_config_json)

    def process_action_config_json(self, action_config_json):
        """
        Process an action configuration into an action instance.
        :param action_config_json: The action JSON configuration.
        """

        if 'name' not in action_config_json:
            raise InvalidActionConfigurationException('Action configuration missing name')

        action_name = action_config_json['name']

        if action_name in self.actions_by_name:
            raise InvalidActionConfigurationException('Action name "{0}" duplicated'.format(action_name))

        if 'action' not in action_config_json:
            raise InvalidActionConfigurationException('Action configuration "{0}" missing action type'.format(action_name))

        action_type = action_config_json['action']

        if action_type not in self.ACTIONS:
            raise InvalidActionConfigurationException('Unknown action: "{0}"'.format(action_name))

        action_class = self.ACTIONS[action_type]

        if action_config_json.get('ignore', False):
            print('==== Ignoring action "{0}".'.format(action_name))
            return

        if not action_class.valid_deploy_env(self.deploy_env):
            print('==== Ignoring action "{0}" due to deploy environment "{1}".'.format(action_name, self.deploy_env))
            return

        action = action_class(action_name, self.config_file_dir, action_config_json, **self.action_kwargs)
        self.actions.append(action)
        self.actions_by_name[action_name] = action

    def is_empty(self):
        return len(self.actions) == 0

    def execute(self, keycloak_client):
        for action in self.actions:
            action.execute(keycloak_client)
