from __future__ import division

import json
import logging
import os
import socket
import base64
from collections import namedtuple
from functools import partial
from functools import wraps

import click
import six
import yaml
from click import exceptions
from missinglink.core.api import ApiCaller
from missinglink.crypto import Asymmetric, MultiKeyEnvelope, SshIdentity
from missinglink_kernel.callback.utilities.source_tracking import GitRepoSyncer
from missinglink.commands.utils import is_windows
from missinglink.legit.path_utils import normalize_path

from .cloud_credentials_handler import CloudCredentialsHandler
from missinglink.commands.utilities.docker_tools.docker_tools_factory import create_docker_tools
from .list_utils import filter_empty_values_from_dict, msgpack_dict
from .options import CommonOptions, OrganizationParamType, ProjectIdParamType
from .path_tools import PathTools

logger = logging.getLogger(__name__)

job_context = namedtuple('JobContext', ['disable_colors', 'attach', 'docker_creds', 'secure_env', 'input_data', 'org', 'project'])


def job_params(fn):
    @wraps(fn)
    @CommonOptions.org_option(required=False)
    @CommonOptions.project_id_option(required=False, help='Project ID to hold the experiments started by the job')
    @click.option('--image', type=str, required=False, help='Docker image to use, defaults to missinglinkai/tensorflow')
    @click.option('--git-repo', type=str, required=False, help='Git repository to pull the code from')
    @click.option('--no-source', type=bool, is_flag=True, required=False, help='Do not pass source code for this job')
    @click.option('--git-tag', type=str, required=False, help='Git branch/tag for the git repository. defaults to master. The cloned code will be available under `/code`')
    @click.option('--source-dir', type=str, required=False, help='source directory for the experiment (if you have configured tracking repository)')
    @click.option('--command', type=str, multiple=True, required=False, help='command to execute')
    @click.option('--gpu/--cpu', required=False, default=None, help='Run this job on GPU. Defaults to True')
    @click.option('--data-volume', type=str, required=False, help='data volume to clone data from')
    @click.option('--queue', type=str, required=False, help='queue to use for this job')
    @click.option('--data-query', type=str, required=False, help='query to execute on the data volume')
    @click.option('--data-dest', type=str, required=False, help='destination folder and format for cloning data. If provided, must begin with /data')
    @click.option('--data-iterator', type=bool, required=False, help='When set to True, data will not be cloned before the experiment and the quarry will be available for the SDK iterator')
    @click.option('--recipe', '-r', type=click.Path(exists=True), required=False, help='recipe file. recipe file is yaml file with the `flag: value` that allows you to specify default values for all params for this function')
    @click.option('--save-recipe', type=str, required=False, help='Saves a recipe for this call to the target file and quits. Note the default values are not encoded into the recipe')
    @click.option('--env', '-e', multiple=True, type=(str, str), default=None, required=False, help='Environment variables to pass for the invocation in key value format. You can use this flag multiple times')
    @click.option('--output-paths', multiple=True, required=False, help='Paths that will be exported to the Data management at the end of the invocation job. The paths will be available to the the running code under `/path_name` by defaults to `/output`')
    @click.option('--git-identity', type=click.Path(exists=True), required=False, default=None, help='[Secure] If provided, the provided path will be used as git (ssh) identity when pulling code. otherwise your default organisation identity will be used')
    @click.option('--persistent-path', multiple=True, type=(str, str), required=False, help='Maps a path local to the server running the job as path inside the docker')
    @click.option('--secure-env', '-se', multiple=True, type=(str, str), required=False, help='[Secure] Provide additional environment variables to the job. The format is  `env_key env_value`')
    @click.option('--docker-host', type=str, default=None, required=False, help='[Secure] if docker login is needed to pull the image, login to this host')
    @click.option('--docker-user', type=str, default=None, required=False, help='[Secure] if docker login is needed to pull the image, login with this user')
    @click.option('--docker-password', type=str, default=None, required=False, help='[Secure] if docker login is needed to pull the image, login with this password')
    @click.option('--requirements-txt', type=str, default=None, required=False, help='Install pip requirements from this path (relative to the repo). defaults to `requirements.txt`')
    @click.option('--disable-colors', is_flag=True, default=None, required=False, help='Disable colors in logs')
    @click.option('--attach', is_flag=True, default=None, required=False, help='Wait and print logs of the submitted job')
    @click.option('--name', '-n', type=str, required=False, help='Specify a name for the job. If not provided, the name will be auto generated')
    @click.option('--name-prefix', '-np', type=str, required=False, help='Specify a prefix for the job name. If the `--name` flag is not provided, a random string will be appended to the prefix as job name')
    def decorated(*args, **kwargs):
        return fn(*args, **kwargs)

    return decorated


class JobParser(CloudCredentialsHandler):
    DEFAULT_RECIPE_PATH = '.ml_recipe.yaml'

    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        self.docker_tools = kwargs.pop('docker_tools', None) or create_docker_tools(ctx, **kwargs)
        self.kwargs = filter_empty_values_from_dict(kwargs)
        self.call_api = partial(ApiCaller.call, self.ctx.obj, self.ctx.obj.session)

    @classmethod
    def _normalise_env_array_to_dict(cls, env_array):
        if env_array is None:
            return {}

        if isinstance(env_array, six.string_types):
            return json.loads(env_array)

        if isinstance(env_array, (dict, list, tuple)):
            return env_array

    @classmethod
    def __strip_starting_quotes(cls, value):
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            return value[1:-1]

        return value

    @classmethod
    def _normalise_env_tuple(cls, env_tuple):
        if isinstance(env_tuple, (tuple, list)):
            key = str(env_tuple[0])
            value = str(env_tuple[1])
        else:
            key, value = env_tuple.split('=')
            value = cls.__strip_starting_quotes(value)
        key = key.strip()
        value = value.strip()
        return key, value

    @classmethod
    def parse_env_array_to_dict(cls, data):
        env_array = cls._normalise_env_array_to_dict(data)
        if isinstance(env_array, dict):
            return dict([cls._normalise_env_tuple(env_tuple) for env_tuple in env_array.items()])

        return dict([cls._normalise_env_tuple(env_tuple) for env_tuple in env_array])

    @classmethod
    def _serialise_env_variables(cls, variables):
        return json.dumps(variables)

    @classmethod
    def _get_default_image(cls, input_data):
        default_docker_image = 'missinglinkai/tensorflow:latest'
        if input_data.get('gpu', True):
            default_docker_image += '-gpu'
        if six.PY3:
            default_docker_image += '-py3'
        logger.debug('Selected %s as default image', default_docker_image)
        return default_docker_image

    def _build_run_args(self):
        env = self.kwargs.pop('env', [])
        persistent_path = self.kwargs.pop('persistent_path', [])
        # persistent_path is [(s,t)] provided by the cli, persistent_paths is [{'host_path':s , 'mount_path': t}] restored from the yaml template
        persistent_paths = self.kwargs.pop('persistent_paths', [])
        if len(persistent_path) > 0:
            persistent_paths = []
            for host_path, mount_path in persistent_path:
                persistent_paths.append(dict(host_path=host_path, mount_path=mount_path))
        image = self.kwargs.pop('image', self._get_default_image(self.kwargs))
        input_data = {
            'org': self.kwargs.pop('org', None),
            'requirements_txt': self.kwargs.pop('requirements_txt', None),
            'project': self.kwargs.pop('project', None),
            'image': image,
            'queue': self.kwargs.pop('queue', None),
            'name_prefix': self.kwargs.pop('name_prefix', None),
            'name': self.kwargs.pop('name', None),
            'no_source': self.kwargs.pop('no_source', None),
            'git_repo': self.kwargs.pop('git_repo', None),
            'git_tag': self.kwargs.pop('git_tag', None),
            'source_dir': self.kwargs.pop('source_dir', None),
            'command': self.kwargs.pop('command', None),
            'data_query': self.kwargs.pop('data_query', None),
            'data_volume': self.kwargs.pop('data_volume', None),
            'data_use_iterator': self.kwargs.pop('data_iterator', self.kwargs.pop('data_use_iterator', None)),
            'data_dest_folder': self.kwargs.pop('data_dest', self.kwargs.pop('data_dest_folder', None)),
            'output_paths': self.kwargs.pop('output_paths', []),
            'persistent_paths': persistent_paths,
            'gpu': self.kwargs.pop('gpu', True),
            'git_identity': self.kwargs.pop('git_identity', None),
            'env': self.parse_env_array_to_dict(env)
        }

        if not input_data['org']:
            input_data['org'] = CommonOptions.fill_value(OrganizationParamType, self.ctx, 'org', 'Select Organization', group_by_org=False)

        if not input_data['project']:
            input_data['project'] = CommonOptions.fill_value(ProjectIdParamType, self.ctx, 'project', 'Select Project', group_by_org=False)

        return input_data

    def _load_recipe(self, r_path):
        r_path = r_path or self.DEFAULT_RECIPE_PATH
        if not os.path.isfile(r_path):
            return {}
        else:
            click.echo('loading defaults from recipe: %s' % r_path, err=True)
            with open(r_path) as f:
                return filter_empty_values_from_dict(yaml.safe_load(f))

    @classmethod
    def _ensure_value(cls, input_data, key):
        if input_data.get(key) is None:
            raise exceptions.UsageError('Please provide `%s`' % key)

    @classmethod
    def _validate_input_data(cls, input_data):
        # Data test must reside inside /data as it will reside inside the data folder, until is configurable
        if not (input_data.get('data_dest_folder', None) or '/data').startswith('/data'):
            raise click.BadOptionUsage('data-des', '--data-dest must begin with /data')

        cls._ensure_value(input_data, 'command')
        cls._ensure_value(input_data, 'project')
        cls._ensure_value(input_data, 'org')

    def _read_input_data_and_load_recipe(self):
        # Load Recipe
        recipe = self.kwargs.pop('recipe', None)
        recipe_data = self._load_recipe(recipe)
        for k, v in recipe_data.items():
            if k not in self.kwargs:
                self.kwargs[k] = v
        # Apply Defaults
        input_data = self._build_run_args()
        self._validate_input_data(input_data)

        return input_data

    def _has_valid_git_pointer(self, input_data):
        logging.debug('is valid git pointer? %s', input_data)

        if input_data.get('no_source', False):
            logger.info('Skipping git src')
            input_data['git_mode'] = 'skip'
            input_data['git_tag'] = None
            input_data['git_repo'] = None
            return True

        is_valid = input_data.get('git_repo') is not None
        if is_valid:
            input_data['git_mode'] = input_data.get('git_mode', 'external')
        return is_valid

    def _handle_src_pointer_error(self, sync_res):
        if 'error' not in sync_res:
            return

        error = sync_res['error']
        if error == 'no tracking repository found.':
            raise exceptions.UsageError('''
Resource Management could not find a git repository to use for the job. In order to run a job do one of the following:
1) Use `--no-source` flag to indicate that no code is needed for this specific job the command  and image are sufficient
2) Provide `--source-dir` - a path managed by git with a .ml_tracking_repo for advanced tracking
3) Use `--git-repo` parameter and specify git url to be used for the job

For more information please visit: https://missinglink.ai/docs/resource-management/advanced-resource-management/inputs-outputs/
            ''')

        raise exceptions.UsageError('Failed to obtain git point to use fo the experiment. The error was %s' % error)

    def build_src_pointer(self, input_data):
        if not self._has_valid_git_pointer(input_data):
            src_repo_state, repo_obj = GitRepoSyncer.source_tracking_data(input_data.get('source_dir'))
            sync_res = GitRepoSyncer.sync_working_dir_if_needed(repo_obj, False)
            self._handle_src_pointer_error(sync_res)
            input_data['git_repo'] = sync_res['remote']
            input_data['git_tag'] = sync_res['branch']
            input_data['git_mode'] = sync_res.get('mode', 'shadow')

        return input_data

    def _save_recipe(self, input_data, save_recipe):
        save_recipe_path = os.path.expanduser(save_recipe)
        with open(save_recipe_path, 'w') as f:
            save_data = filter_empty_values_from_dict(input_data)
            yaml.safe_dump(save_data, f, default_flow_style=False)
            click.echo(yaml.safe_dump(save_data, default_flow_style=False))
            click.echo('Recipe saved to {}'.format(save_recipe))

        return True

    def _get_docker_creds(self):
        user = self.kwargs.pop('docker_user', None)
        password = self.kwargs.pop('docker_password', None)
        endpoint = self.kwargs.pop('docker_host', None)
        if endpoint is not None and password is not None:
            return dict(user=user, password=password, endpoint=endpoint)

        return None

    def _get_secure_env(self):
        envs = self.kwargs.pop('secure_env', None) or ()
        res = {}
        for item in envs:
            k, v = item
            res[k] = v
        return res

    def prepare_job_context(self):

        input_data = self.parse_input_data()
        if input_data is None:
            # this was save recipe
            return None

        return job_context(
            disable_colors=self.kwargs.pop('disable_colors', False),
            attach=self.kwargs.pop('attach', False),
            docker_creds=self._get_docker_creds(),
            secure_env=self._get_secure_env(),
            input_data=input_data,
            org=input_data.pop('org'),
            project=input_data.pop('project')
        )

    def parse_input_data(self):
        save_recipe = self.kwargs.pop('save_recipe', False)
        input_data = self._read_input_data_and_load_recipe()

        if save_recipe:
            self._save_recipe(input_data, save_recipe)
            return

        self.build_src_pointer(input_data)
        input_data = filter_empty_values_from_dict(input_data)
        click.echo(err=True)
        click.echo('Job parameters:', err=True)
        click.echo(yaml.safe_dump(input_data, default_flow_style=False), err=True)
        click.echo(err=True)
        input_data['env'] = self._serialise_env_variables(input_data.get('env', {}))
        return input_data

    def _secure_identity(self, data, git_identity):
        if git_identity:
            data.append(
                {
                    'type': 'file',
                    'path': '@identity',
                    'data': SshIdentity(git_identity).export_private_key_bytes()
                })

    def _secure_docker_creds(self, data, docker_creds):
        if docker_creds:
            data.append(
                {
                    'type': 'docker',
                    'path': '{}'.format(docker_creds['endpoint']).encode('utf-8'),
                    'data': '{};{}'.format(docker_creds['user'], docker_creds['password']).encode('utf-8')
                })

    def _secure_env_vars(self, data, secure_env):
        if not secure_env:
            return

        for k, v in secure_env.items():
            data.append(
                {
                    'type': 'env',
                    'path': k.encode('utf-8'),
                    'data': v.encode('utf-8')
                })

    def prepare_encrypted_data(self, org, input_data, docker_creds, secure_env):
        secure_data = []
        self._secure_identity(secure_data, input_data.get('git_identity'))
        self._secure_docker_creds(secure_data, docker_creds)
        self._secure_env_vars(secure_data, secure_env)

        if not secure_data:
            return

        encryption_keys = self.call_api('get', '{}/run/security_credentials'.format(org))
        data_dict = {'data': secure_data, 'encryption_path': encryption_keys['keys']}
        ssh_keys = [Asymmetric(key) for key in encryption_keys['keys']]
        cipher = MultiKeyEnvelope(*ssh_keys)

        # this encrypts *to* string, rather than *from* string
        input_data['encrypted_data'] = cipher.encrypt_string(msgpack_dict(data_dict))
        return input_data

    def submit_job(self, job_env):
        result = self.call_api('put', '{}/{}/invoke'.format(job_env.org, job_env.project), job_env.input_data)
        result['job'] = result.pop('job', result.pop('invocation', None))
        return result

    @classmethod
    def _command_extent_with_secure(cls, command, job_env):
        cls.command_extend_from_iter(command, 'env', sorted(job_env.secure_env.items()))
        if job_env.docker_creds:
            cls.command_extend_from_iter(command, 'docker-auth', [(job_env.docker_creds['endpoint'], job_env.docker_creds['user'], job_env.docker_creds['password'])])

    def _validate_memory(self, input_data):
        stats = self.docker_tools.client.info()
        target_memory_warning = 6 if input_data.get('gpu', True) else 1.5
        mem_in_gb = stats.get('MemTotal') / 1073741824  # 1024 ^2
        mem_in_gb = round(mem_in_gb, 2)
        logger.info('Memory available to the docker server %s GB', mem_in_gb)
        if mem_in_gb < target_memory_warning:
            click.echo('The memory of the docker server on this host is limited to %s GB. This is below the recommended limit of %s GB and my cause jobs to fail.' % (mem_in_gb, target_memory_warning), err=True)

    def _validate_gpu_params(self, input_data):
        if not input_data.get('gpu', False) or self.docker_tools.gpu_count() > 0:
            return

        click.echo('Defaulting to CPU execution - there is no GPU configured on this host', err=True)
        input_data['gpu'] = False
        self._downgrade_gpu_image(input_data)

    @classmethod
    def _remove_gpu_tag(cls, image):
        if ':' not in image:
            return image

        image_parts = image.split(':')
        tag = image_parts[-1]
        if 'gpu' not in tag:
            return image

        tag = tag.replace('gpu', '').replace('--', '-')
        if tag.endswith('-'):
            tag = tag[:-1]
        if tag.startswith('-'):
            tag = tag[1:]
        image_parts[-1] = tag
        return ':'.join(image_parts)

    @classmethod
    def _image_downgrade_supported(cls, image):
        if '/' not in image:
            return False
        domain = image.split('/')[0]
        return domain in ['missinglinkai', 'tensorflow']

    def _downgrade_gpu_image(self, input_data):
        original_image = input_data['image']
        if self._image_downgrade_supported(original_image):
            image = self._remove_gpu_tag(original_image)
            input_data['image'] = image
            click.echo('image %s changed to %s due to lack of GPU on the host machine' % (original_image, image), err=True)
        elif 'gpu' in original_image.lower():
            click.echo('You are running in CPU mode but it seems your image (%s) is for GPU' % original_image, err=True)

    def _get_docker_volumes(self, cache_volume):
        rm_volumes = self.docker_tools.get_run_mounts()
        rm_volumes[cache_volume] = {'bind': normalize_path('/cache')}
        return rm_volumes

    def build_local_command(self, job_env):
        self.validate_no_running_containers()
        job_env.input_data['unscheduled'] = True
        self._validate_memory(job_env.input_data)
        self._validate_gpu_params(job_env.input_data)

        job_response = self.submit_job(job_env)
        token = self.docker_tools.auth_resource(job_env.org)
        prefix, config_data = self.docker_tools.get_config_prefix_and_file(self.ctx.obj.config)
        ssh_file_path = job_env.input_data.pop('git_identity', PathTools.get_ssh_path())
        command = []
        command.extend(['job'])
        command.extend(['--hostname', socket.gethostname()])
        command.extend(['--token', token])
        command.extend(['--job', job_response['job']])
        command.extend(['--ml-server', self.docker_tools.config.rm_socket_server])

        if prefix is not None:
            command.extend(['--ml-config-prefix', prefix])
        command.extend(['--ml-config-file', Asymmetric.bytes_to_b64str(config_data)])
        command.extend(['--ml-backend', self.docker_tools.config.ml_backend])

        self._add_ssh_private_key_command(command, ssh_file_path)

        self.extend_command_with_creds(command)
        self._command_extent_with_secure(command, job_env)

        self.docker_tools.ensure_rms_volumes(False)
        cache_volume = self.docker_tools.ensure_cache_volume_present()

        rm_env = self._build_local_docker_env(prefix)

        command_params = {
            'command': ' '.join([str(x) for x in command]),
            'image': self.docker_tools.config.rm_manager_image,
            'auto_remove': True,
            'environment': rm_env,
            'name': self.docker_tools.config.rm_container_name,
            'detach': True,
            'volumes': self._get_docker_volumes(cache_volume),
        }

        return job_response['job'], command_params

    @staticmethod
    def _add_ssh_private_key_command(command, ssh_file_path):
        try:
            ssh_private_key = SshIdentity(ssh_file_path).export_private_key_bytes()
        except IOError:
            ssh_private_key = None

        if not ssh_private_key:
            logger.debug('No ssh private key found.')
            return

        if is_windows():
            command.extend(['--ssh-private-key-b64', base64.b64encode(ssh_private_key).decode('utf-8')])
        else:
            command.extend(['--ssh-private-key', "'%s'" % ssh_private_key.decode('utf-8')])

    def run_docker(self, command):
        return self.docker_tools.client.containers.run(**command)

    def _build_local_docker_env(self, prefix):
        rm_env = {
            'ML_CONFIG_VOLUME': self.docker_tools.config.rm_config_volume,
            'ML_PIP_INDEX': os.environ.get('ML_PIP_INDEX', ''),
            'ML_PIP_VERSION': '',
            'ML_PIP_CACHE_DIR': normalize_path('/cache/pip_cache'),
            'ML_RM_VENV_DIR': normalize_path('/cache/rm_venv'),
        }
        if prefix:
            del (rm_env['ML_PIP_CACHE_DIR'])
            rm_env['ML_PIP_INDEX'] = 'https://test.pypi.org/simple/'
            rm_env['ML_PIP_VERSION'] = '>=2.6'

        return rm_env

    def validate_no_running_containers(self):
        running_containers = self.docker_tools.running_ml_containers()
        logger.info('Current RM containers: %s', running_containers)
        if running_containers:
            click.echo('There is an active resource manger or active jobs running. The containers are:', err=True)
            for container in running_containers:
                click.echo(' | '.join([container.id, container.display]), err=True)

            raise click.Abort('There are resource manager containers present')
