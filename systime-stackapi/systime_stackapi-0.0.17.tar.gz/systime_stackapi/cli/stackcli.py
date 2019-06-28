import os
import sys
import click
from fcache.cache import FileCache
from pprint import pprint

from systime_stackapi.stackDiscovery import StackDiscovery
from systime_stackapi.stackService import StackService

CONTEXT_SETTINGS = dict(auto_envvar_prefix='SYSTIME_STACK_CLI')


class Context(object):

    def __init__(self):
        self.verbose = False
        self.key_name = os.getenv('SYSTIME_STACK_CLI_KEY_NAME')
        self.key = os.getenv('SYSTIME_STACK_CLI_KEY')
        self.stack_hostname = None
        self.stack_helper = StackHelper()

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)

pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          'commands'))


class StackCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('systime_stackapi.cli.commands.cmd_' + name,
                             None, None, ['cli'])
        except ImportError:
            return
        return mod.cli

class StackHelper(object):
    def __init__(self):
        self.key_name = os.getenv('SYSTIME_STACK_CLI_KEY_NAME')
        self.key = os.getenv('SYSTIME_STACK_CLI_KEY')
        self.stack_hostname = None
        self._stack_services = None
        self._stack_installations = None
        self.cache = FileCache('stackcli')

    @property
    def stack_services(self):
        if self.key_name is None or self.key is None:
            self.log('Please provide a key_name and key, either by environment variable or parameter.')
            self.log('Recommended approach is settings the following env vars: SYSTIME_STACK_CLI_KEY_NAME, SYSTIME_STACK_CLI_KEY.')
            exit(1)

        if self._stack_services is not None:
            return self._stack_services

        hostnames = self.stack_hostname
        if hostnames is None:
            hostnames = self.get_stack_hostnames()

        self._stack_services = {}

        discovery = StackDiscovery(domain='systime.dk')
        for hostname in hostnames:
            endpoint = discovery.get_stack_endpoint(hostname)
            service = StackService(endpoint, self.key_name, self.key)
            self._stack_services[endpoint] = service

        return self._stack_services


    def get_stack_hostnames(self):
        discovery = StackDiscovery(domain='systime.dk')
        return discovery.stack_list()

    def stack_endpoint_from_installation(self, installation):
        stacks = self.build_installation_structure().keys()
        for stack in stacks:
            for entry in self._stack_installations[stack]:
                if entry['InstallationName'] == installation:
                    return stack

        raise exception('Installation stack could not be found')

    def get_installation_webservers(self, installation):
        stack_endpoint = self.stack_endpoint_from_installation(installation)

        for key, service in self.stack_services.items():
            if stack_endpoint == key:
                return(service.webserver_list())

        raise exception('Installation stack could not be found')

    def build_installation_structure(self):
        if self._stack_installations is None:
            self._stack_installations = {}

            for stack_service in self.stack_services.values():
                self._stack_installations[stack_service.service_url] = stack_service.installations_list()

        return self._stack_installations

    def get_installations(self):
        all_installations = []

        for installations in self.build_installation_structure().values():
            all_installations += installations

        return all_installations

    def stack_hostname_cache_key(self):
        if self.stack_hostname is not None:
            return self.stack_hostname

        return ''

    def get_installation_name_list(self, use_cache=False):
        hashkey = self.stack_hostname_cache_key()
        cache_key = '{}_{}'.format('installation_name_list', hashkey)

        if use_cache is True and self.cache.get(cache_key) is not None:
            return self.cache[cache_key]

        name_list = []

        installations = self.get_installations()
        for install in installations:
            name_list.append(install['InstallationName'])

        self.cache[cache_key] = name_list
        self.cache.sync()

        return name_list

stack_helper = StackHelper()

@click.command(cls=StackCLI, context_settings=CONTEXT_SETTINGS)
@click.option('--stack-hostname', type=click.Choice(choices=stack_helper.get_stack_hostnames()),
             help='Limits to specific stack.')
@click.option('--key-name', help='Name of access key.')
@click.option('--key', help='Access key.')
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@pass_context
def cli(ctx, verbose, key_name, key, stack_hostname):
    """A CLI for the systime Stack."""
    ctx.verbose = verbose
    if key_name is not None:
        ctx.key_name = key_name
    if key is not None:
        ctx.key = key
    if stack_hostname is not None:
        ctx.stack_hostname = stack_hostname

if __name__== "__main__":
    cli()
