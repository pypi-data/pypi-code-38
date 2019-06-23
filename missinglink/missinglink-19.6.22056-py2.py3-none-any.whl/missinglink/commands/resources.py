# -*- coding: utf-8 -*-
import click

from .utilities import CommonOptions, CloudCredentialsHandler
from missinglink.core.api import ApiCaller
from missinglink.commands.commons import output_result
from colorama import Fore, Style
import six
from collections import defaultdict
from pprint import pformat
from missinglink.commands.cloud.backend_context import BackendContext
from missinglink.commands.utilities.docker_tools import create_docker_tools


@click.group('resources', help='Resource Management')
def resources_commands():
    pass


@resources_commands.group('local-grid')
def local_grid():
    pass


def _trim_value(value, max_chars=30):
    if len(value) > max_chars:
        return value[:max_chars - 4] + ' ...'

    return value


def _with_format(text, fore='', style=''):
    return Style.RESET_ALL + fore + style + text + Style.RESET_ALL


class ArgRow:
    show_score = {
        'std': 1000,
        'adv': 500,
        'internal': 100
    }
    readonly_score = {
        False: 0,
        True: 50
    }
    configured_score = {
        False: 0,
        True: 5000
    }

    @classmethod
    def _values_to_str(cls, v):
        if isinstance(v, six.string_types):
            return v

        return '\n'.join(v if v is not None else '')

    def _active_value(self):
        return self.value if self.configured or self.read_only else self.default_value

    def __eq__(self, other):
        return self.name == other.name and self.arg == other.arg

    def __init__(self, name, arg):
        self.name = name
        self.arg = arg
        self.read_only = self.arg.get('read_only', False)
        self.configured = 'configured' in self.arg and not self.read_only
        self.show_level = self.arg.get('show_level', self.arg.get('edit_level', 'internal'))
        self.score = self.show_score[self.show_level] + self.configured_score[self.configured] + self.readonly_score[self.read_only]

        self.value = self._values_to_str(self.arg.get('configured'))
        self.default_value = self._values_to_str(self.arg.get('default'))
        self.active_value = self._active_value()

    color_legend = '  |  '.join(['Color Legend:', _with_format('read only', Fore.BLUE), _with_format('configured', Fore.GREEN), _with_format('default value', Fore.RESET)])
    param_filed = _with_format('Parameter', Fore.WHITE, Style.BRIGHT)
    value_field = _with_format('Value', Fore.WHITE, Style.BRIGHT)
    default_field = _with_format('Default', Fore.WHITE, Style.DIM)
    description_field = _with_format('Description', Fore.WHITE, Style.DIM)

    def configured_name(self):
        return _with_format(self.name, Fore.GREEN, Style.BRIGHT)

    def default_name(self):
        return _with_format(self.name, Fore.RESET, Style.BRIGHT)

    def row_name(self):
        return self.configured_name() if self.configured else self.default_name()

    def read_only_value(self):
        return _with_format(self.active_value, Fore.BLUE, Style.NORMAL)

    def configured_value(self):
        return _with_format(self.active_value, Fore.GREEN, Style.BRIGHT)

    def un_configured_value(self):
        return _with_format(self.active_value, Fore.RESET, Style.DIM)

    def configured_default_value(self):
        return _with_format(self.default_value, Fore.GREEN, Style.BRIGHT)

    def un_configured_default_value(self):
        return _with_format(self.default_value, Fore.RESET, Style.DIM)

    def row_value(self):
        if self.read_only:
            return self.read_only_value()

        if self.configured:
            return self.configured_value()

        return self.un_configured_value()

    def description_all(self):
        return _with_format(_trim_value(self.arg.get('description'), 60), Style.DIM)

    def row_description(self):
        return self.description_all()

    def row_default(self):
        if self.read_only:
            return ''

        if self.configured:
            return self.un_configured_default_value()

        return self.configured_default_value()

    def to_row(self):
        return {
            self.param_filed: self.row_name(),
            self.value_field: self.row_value(),
            self.default_field: self.row_default(),
            self.description_field: self.row_description(),
        }

    def displayed(self, target_show_levels, configured_only):
        if self.configured:
            return True

        shown = self.show_level in target_show_levels
        return shown and not configured_only

    @classmethod
    def import_and_filter(cls, data, target_show_levels, configured_only):
        res = []
        for k, v in data.items():
            ob = cls(k, v)
            if ob.displayed(target_show_levels, configured_only):
                res.append(ob)

        return res

    @classmethod
    def table_fields(cls, kwargs):
        show_defaults = kwargs.get('show_defaults', False)
        show_description = kwargs.get('show_description', False)

        fields = [cls.param_filed, cls.value_field]
        if show_defaults:
            fields.append(cls.default_field)
        if show_description:
            fields.append(cls.description_field)

        return fields

    @classmethod
    def print_table(cls, ctx, kwargs, data):
        table = [x.to_row() for x in sorted(data, key=lambda x: x.score, reverse=True)]
        fields = cls.table_fields(kwargs)
        click.echo(cls.color_legend)
        click.echo()
        output_result(ctx, table, fields=fields)

    @classmethod
    def parse_user_input(cls, tuples, unset_items):
        res = defaultdict(list)
        for key, value in tuples:
            res[key].append(value)
            if 'None' in res[key]:
                res[key] = ['None']
        for item in unset_items:
            res[item] = ['None']

        return dict(res)


@local_grid.command('init', help='Initialize Resource Management on a local server.')
@click.pass_context
@CommonOptions.org_option()
@click.option('--ssh-key-path', type=str, help='Path to the private ssh key to be used by the resource manager.', default=None)
@click.option('--force/--no-force', default=False, help='Force installation (stops current resource manager if present).')
@click.option('--resource-token', default=None, type=str, help='MissingLink resource token. One will be generated if this instance of MissingLink is authorized.')
# cloud creds
@click.option('--link-aws/--no-aws-link', required=False, default=True,
              help='When configuring the aws-cli, an .aws folder is created in your home directory. The folder contains your AWS credentials. When “linked,” the folder will be mounted in your jobs and Resource Manager, allowing them to use the credentials of the host to access AWS services. Defaults to `--link-aws`.')
@click.option('--env-aws/--no-aws-env', required=False, default=True, help='Similar to the .aws folder, AWS allows authentication using environment variables. Defaults to `--env-aws`.')
@click.option('--link-gcp/--no-gcp-link', required=False, default=True, help='Similar to AWS, GCP also has its default directory and this flag allows the folder to be mounted in your jobs and Resource Manager to call GCP APIs. Defaults to `--link-gcp`.')
@click.option('--link-azure/--no-azure-link', required=False, default=True, help='Similar to AWS, Azure also has its default directory and this flag allows the folder to be mounted in your jobs and Resource Manager to call Azure APIs. Defaults to `--link-azure`.')
@click.option('--capacity', required=False, default=1, help='Specifies the maximum number of jobs that run concurrently on this server.')
@click.option('--cache-path', type=str, required=False, help='Path for pip, conda and MissingLink caches')
def install_rm(ctx, org, ssh_key_path, force, resource_token, capacity=None, cache_path=None, **kwargs):
    cred_sync = CloudCredentialsHandler(kwargs)
    docker_tools = create_docker_tools(ctx, cloud_credentials=cred_sync)

    docker_tools.pull_rm_image()
    docker_tools.validate_no_running_resource_manager(force)
    docker_tools.validate_local_config(org=org, force=force, ssh_key_path=ssh_key_path, token=resource_token, capacity=capacity, cache_path=cache_path)

    docker_tools.run_resource_manager()
    click.echo('The resource manager is configured and running')


def restore_template_options(func):
    @click.option('--ssh', type=(str, str, str), help='ssh key data', required=True)
    @click.option('ml', '--ml', '--mali', type=(str, str, str), help='mali config data', required=True)
    @click.option('--prefix', type=str, help='ml prefix type', required=False)
    @click.option('--token', type=str, help='ml prefix type', required=True)
    @click.option('--rm-socket-server', type=str, help='web socket server', required=True)
    @click.option('--rm-manager-image', type=str, required=True)
    @click.option('--rm-config-volume', type=str, required=True)
    @click.option('--rm-container-name', type=str, required=True)
    @click.option('--ml-backend', type=str, required=True)
    @click.option('--cache-path', type=str, required=False, help='Path for pip, conda and MissingLink caches')
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

    return wrapper


@resources_commands.command('restore-aws-template', help="restores predefined cloud configuration", hidden=True)
@click.pass_context
@click.option('--arn', type=str, help='arn of the KMS encryption key', required=True)
@restore_template_options
def apply_aws_template(
        ctx, arn, ssh, ml, prefix, token, rm_socket_server, rm_manager_image,
        rm_config_volume, rm_container_name, ml_backend, cache_path):
    from .cloud.aws import AwsContext
    if prefix == str(None):
        prefix = None

    click.echo('decrypting data')
    kms = AwsContext.get_kms(arn)
    ssh_key = AwsContext.decrypt(kms, ssh).decode('utf-8')
    ml_data = AwsContext.decrypt(kms, ml).decode('utf-8')
    run_docker(ctx, ml_backend, ml_data, prefix, rm_config_volume, rm_container_name, rm_manager_image,
               rm_socket_server, ssh_key, token, None, cache_path)


@resources_commands.command('restore-azure-template', help="restores predefined cloud configuration", hidden=True)
@click.pass_context
@click.option('--key', type=str, help='Key id of Key Vault encryption key', required=True)
@click.option('--role_id', type=str, help='MSI id used to connect ot Key Vault', required=True)
@restore_template_options
def apply_azure_template(
        ctx, key, role_id, ssh, ml, prefix, token, rm_socket_server, rm_manager_image,
        rm_config_volume, rm_container_name, ml_backend, cache_path):
    from .cloud.azure import AzureContext
    if prefix == str(None):
        prefix = None

    click.echo('decrypting data')
    kms = AzureContext.get_cloud_kms(key, role_id)
    ssh_key = AzureContext.decrypt(kms, ssh).decode('utf-8')
    ml_data = AzureContext.decrypt(kms, ml).decode('utf-8')
    run_docker(ctx, ml_backend, ml_data, prefix, rm_config_volume, rm_container_name, rm_manager_image,
               rm_socket_server, ssh_key, token, env={'ML_INSTANCE_ROLE': role_id}, cache_path=cache_path)


def run_docker(ctx, ml_backend, ml_data, prefix, rm_config_volume, rm_container_name, rm_manager_image,
               rm_socket_server, ssh_key, token, env=None, cache_path=None):
    click.echo('building installation config')
    docker_tools = create_docker_tools(ctx, rm_socket_server=rm_socket_server, rm_manager_image=rm_manager_image,
                                       rm_config_volume=rm_config_volume, rm_container_name=rm_container_name,
                                       ml_backend=ml_backend)
    click.echo('pulling RM')
    docker_tools.pull_rm_image()

    click.echo('killing RM')
    docker_tools.validate_no_running_resource_manager(True)

    docker_tools.setup_rms_volume(ssh_key, token, prefix=prefix, ml_data=ml_data, env=env, force=True, cache_path=cache_path)
    docker_tools.remove_current_rm_servers()
    inst = docker_tools.run_resource_manager(env)
    click.echo('The resource manager is configured and running %s' % inst.id)
    click.echo('docker logs -f %s ' % rm_container_name)


def _build_queue_update(kwargs):
    disable = kwargs.pop('disable', None)
    display = kwargs.pop('display', None)
    description = kwargs.pop('description', None)
    disabled = None
    if disable is not None:
        disabled = disable == str(True)
    return {k: v for k, v in {'disabled': disabled, 'display': display, 'description': description}.items() if v is not None}


@resources_commands.command('queue', help="manage resource queues")
@CommonOptions.org_option()
@click.argument('name', required=True, nargs=1)
@click.option('--create', is_flag=True, help='Create new resources queue')
@click.option('--description', type=str, help='Update the description of the given queue')
@click.option('--new-name', 'display', help='Update the name of the given queue to this name')
@click.option('--disable/--enable', is_flag=True, help='Disable existing queue')
@click.pass_context
def manage_queue(ctx, create=None, name=None, **kwargs):
    updates = _build_queue_update(kwargs)
    backend = BackendContext(ctx, kwargs)

    if create:
        result = backend.create_queue(name, updates)
    elif updates:
        result = backend.update_queue(name, updates)
    else:
        result = backend.get_queue(name)

    output_result(ctx, result)


@resources_commands.command('group', help='Show and manage server groups')
@CommonOptions.org_option()
@click.argument('group', required=True, nargs=1)
@click.option('--advanced', required=False, default=False, help="Show advanced configuration parameters as well")
@click.option('--show-defaults/--no-defaults', required=False, default=False, help="Also show default values")
@click.option('--create', required=False, default=None, type=click.Choice(['aws', 'local', 'azure']), help="Create new aws/azure/local group")
@click.option('--show-description/--no-description', required=False, default=False, help="Also show parameter descriptions")
@click.option('--configured-only/--configured-and-defaults', required=False, default=False, help="Show only parameters with configured values.")
@click.option('--set', required=False, default=None, type=(str, str), multiple=True, help="Set parameter value. Some parameters can be specified multiple times for arrays.")
@click.option('--unset', required=False, default=[], type=str, multiple=True, help="Reset parameter value. If the same parameter is specified in both `--set` and `--unset`, it will be unset")
@click.pass_context
def resource_group(ctx, **kwargs):
    group_id = kwargs.pop('group')
    json = 'json' == ctx.obj.output_format

    configured_only = kwargs.get('configured_only', False)
    target_show_levels = ['std']

    if kwargs['advanced']:
        target_show_levels = ['std', 'adv']
    backend = BackendContext(ctx, kwargs)

    new_values = ArgRow.parse_user_input(kwargs['set'], kwargs['unset'])
    create_cloud_type = kwargs.pop('create')
    if new_values or create_cloud_type is not None:
        response = backend.put_resource_group_parameters(group_id, new_values, new_cloud_type=create_cloud_type)
    else:
        response = backend.resource_group_description(group_id)

    return __print_result(ctx, kwargs, response, json, target_show_levels, configured_only)


def __print_result(ctx, kwargs, response, json, target_show_levels, configured_only):
    data = ArgRow.import_and_filter(response, target_show_levels, configured_only)
    if json:
        click.echo(pformat({v.name: v.arg for v in data}))
    else:
        ArgRow.print_table(ctx, kwargs, data)


@local_grid.command('change-group', help='Change the group a server is assigned to')
@CommonOptions.org_option()
@click.argument('server', type=str, required=True)
@click.option('--new-group', required=True, type=str, help="The group to assign the server to")
@click.pass_context
def change_local_server(ctx, server=None, new_group=None, **kwargs):
    backend = BackendContext(ctx, kwargs)
    response = backend.change_local_server(server, new_group)
    output_result(ctx, response)


def __normalise_tuple(tup, i):
    if isinstance(tup, dict):
        return (tup['key'], tup['value'])

    elif not isinstance(tup, (tuple, list)):
        return (str(i), tup)

    return tup


def __add_tup_to_res(t, key_template, res):
    key = key_template % str(t[0])
    value = t[1]

    if isinstance(value, list):
        res.update(_tuples_to_rows(value, prefix=key))
    elif isinstance(value, dict):
        res.update(_tuples_to_rows(value.items(), prefix=key))
    else:
        res[key] = str(value)


def _tuples_to_rows(tuples, prefix=None):
    key_template = '%s' if not prefix else '.'.join([prefix, '%s'])
    res = {}
    i = 0
    for tup in tuples:
        t = __normalise_tuple(tup, i)
        __add_tup_to_res(t, key_template, res)
        i += 1
    return res


def _print_job(ctx, job):
    if job is None:
        return
    rows = [{'key': key, 'value': value} for key, value in _tuples_to_rows(job.items()).items() if not key.startswith('env.ML_')]
    rows = sorted(rows, key=lambda x: x['key'])
    output_result(ctx, rows)


@resources_commands.command('job', help="get job state")
@CommonOptions.org_option()
@click.argument('name', required=True, nargs=1)
@click.pass_context
def get_job(ctx, org=None, name=None):
    url = '{}/job/{}'.format(org, name)
    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', url)
    json = 'json' == ctx.obj.output_format
    if json:
        output_result(ctx, result)
    else:
        _print_job(ctx, result.get('data'))
