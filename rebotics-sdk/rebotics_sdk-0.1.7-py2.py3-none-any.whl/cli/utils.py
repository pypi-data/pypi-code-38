import json
import os

import click
import six

from ..providers import RetailerProvider
from ..utils import mkdir_p

if six.PY2:
    FileNotFoundError = IOError

app_dir = click.get_app_dir('rebotics-scripts')
mkdir_p(app_dir)


class DumpableConfiguration(object):
    def __init__(self, path):
        self.path = path

    @property
    def filepath(self):
        return os.path.expanduser(self.path)

    @property
    def config(self):
        try:
            with open(self.filepath, 'r') as config_buffer:
                return json.load(config_buffer)
        except FileNotFoundError:
            self.config = {}
            return {}
        except (json.JSONDecodeError,):
            return {}

    @config.setter
    def config(self, value):
        with open(self.filepath, 'w') as config_buffer:
            json.dump(value, config_buffer, indent=2)

    def update_configuration(self, key, **configuration):
        current_configuration = self.config
        if key not in current_configuration:
            current_configuration[key] = configuration
        else:
            current_configuration[key].update(configuration)
        self.config = current_configuration


class ReboticsScriptsConfiguration(DumpableConfiguration):
    def __init__(self, path, provider_class=RetailerProvider):
        super(ReboticsScriptsConfiguration, self).__init__(path)
        self.provider_class = provider_class

    def get_provider(self, key):
        config = self.config.get(key, None)
        if config is None:
            return None

        provider_kwargs = {
            'host': config['host'],
            'role': key,
        }
        if 'token' in config:
            provider_kwargs['token'] = config['token']

        provider = self.provider_class(**provider_kwargs)
        return provider


class ReboticsCLIContext(object):
    configuration_class = ReboticsScriptsConfiguration

    def __init__(self, retailer, format, verbose, config_path, provider_class):
        self.key = retailer
        self.format = format
        self.verbose = verbose
        self.config_path = config_path
        self.provider_class = provider_class
        self.config = self.configuration_class(self.config_path, self.provider_class)

    @property
    def provider(self):
        return self.config.get_provider(self.key)

    def update_configuration(self, **configuration):
        self.config.update_configuration(self.key, **configuration)


pass_rebotics_context = click.make_pass_decorator(ReboticsCLIContext, True)

states = DumpableConfiguration(os.path.join(app_dir, 'command_state.json'))


def read_saved_role(command_name):
    roles = states.config.get('roles')
    if roles is None:
        return None
    role = roles.get(command_name)
    if role is not None:
        click.echo('Using previous role: {}'.format(role))
    return role


def process_role(ctx, role, command_name):
    if role is None:
        if ctx.invoked_subcommand != 'roles':
            click.echo('You have not specified role to use. User `roles` subcommand to see what roles are available')
            ctx.exit(1)
    else:
        states.update_configuration('roles', **{command_name: role})
