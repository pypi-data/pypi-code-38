import logging
from collections import namedtuple

import click
import requests
import six
import docker
import docker.errors as docker_errors

from missinglink.core.api import ApiCaller
from missinglink.legit.path_utils import normalize_path

from missinglink.commands.utilities.path_tools import PathTools

logger = logging.getLogger(__file__)

rm_config = namedtuple('RmConfig', ['rm_socket_server', 'rm_manager_image', 'rm_config_volume', 'rm_container_name', 'ml_backend',
                                    'rm_commands_volume'])
running_ml_container = namedtuple('RunningRmContainer', ['id', 'name', 'display', 'container'])


class DockerTools(object):
    CUDA_BASE_IAMGE = 'nvidia/cuda:9.0-base'

    # This volume is used in order to pass commands via files on the mount, in order to deal with command length limit
    # in windows. It is currently supported only in non-docker mali setup of RM.
    ML_COMMANDS_VOLUME = 'ml_commands'

    @classmethod
    def get_config_prefix_and_file(cls, config):
        with open(config.config_file_abs_path, 'rb') as f:
            config_data = f.read()
        prefix = None
        if config.config_prefix is not None:
            prefix = config.config_prefix
        return prefix, config_data

    ADMIN_VOLUME = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock'}}
    DOCKER_IMAGE = 'docker:latest'

    @classmethod
    def _get_combined_volume_path(cls, *args):
        res = {}
        for a in args:
            res.update(a)

        return res

    def __init__(self, ctx, cloud_credentials=None, **kwargs):
        self.ctx = ctx
        self.cloud_credentials = cloud_credentials
        self.config = rm_config(
            rm_socket_server=kwargs.pop('rm_socket_server', self.ctx.obj.config.rm_socket_server),
            rm_manager_image=kwargs.pop('rm_manager_image', self.ctx.obj.config.rm_manager_image),
            rm_container_name=kwargs.pop('rm_container_name', self.ctx.obj.config.rm_container_name),
            rm_config_volume=kwargs.pop('rm_config_volume', self.ctx.obj.config.rm_config_volume),
            rm_commands_volume=kwargs.pop('rm_commands_volume', self.ML_COMMANDS_VOLUME),
            ml_backend=kwargs.pop('ml_backend', self.ctx.obj.config.api_host),
        )

        self._client = kwargs.pop('client', None)

    @staticmethod
    def _get_docker_client():
        return docker.from_env()

    @property
    def client(self):
        if self._client is None:
            logger.info('validating docker')
            self._client = self.validate_and_get_docker_client()

        return self._client

    def pull_image(self, image, msg=None):
        click.echo(msg or ('Pulling docker image: %s' % image), err=True)
        return self.client.images.pull(image)

    def pull_rm_image(self):
        click.echo('Getting/updating MissingLinks Resource Manager image', err=True)
        img = self.pull_image(self.config.rm_manager_image)
        return img

    def _api_call(self, *args, **kwargs):
        return ApiCaller.call(self.ctx.obj, self.ctx.obj.session, *args, **kwargs)

    def auth_resource(self, org):
        return self._api_call('get', '{org}/resource/authorise'.format(org=org)).get('token')

    @classmethod
    def validate_and_get_docker_client(cls):
        try:
            client = cls._get_docker_client()
            client.ping()
        except docker_errors.DockerException as ex:
            raise click.BadArgumentUsage('Docker: Failed to connect to docker host %s' % (str(ex)))
        except requests.exceptions.ConnectionError as ex:
            raise click.BadArgumentUsage('Docker: Failed to connect to docker host %s' % (str(ex)))

        logging.info('Docker host verified')

        return client

    @classmethod
    def _docker_present_return_instance(cls, command, *args, **kwargs):
        import docker.errors as docker_errors

        try:
            return command(*args, **kwargs)
        except docker_errors.NotFound:
            pass

    @classmethod
    def _docker_present(cls, command, *args, **kwargs):
        import docker.errors as docker_errors

        try:
            return command(*args, **kwargs) or True  # we are looking only for exceptions here
        except docker_errors.NotFound:
            return False

    def validate_no_running_resource_manager(self, force):
        current_rm = self._docker_present_return_instance(self.client.containers.get, self.config.rm_container_name)
        if current_rm is None:
            return

        if not force:
            raise click.UsageError('Can not install resource manger while one is running. run `docker kill {}` do stop and reuse config or re-run with `--force` flag to clear all configuration'.format(current_rm.name))

        click.echo('Killing current Resource Manger (%s) due to --force flag' % current_rm.id)
        if current_rm.status == 'running':
            current_rm.kill()

        current_rm.remove(force=True)

    @classmethod
    def export_key_from_path(cls, ssh_key_path):
        from missinglink.crypto import SshIdentity

        return SshIdentity(ssh_key_path).export_private_key_bytes()

    def validate_local_config(self, org, force, ssh_key_path, token, capacity, cache_path):

        ssh_key = None
        if (not self.config_volume_if_present() or force) and ssh_key_path is None:
            ssh_key_path = click.prompt(text='SSH key path (--ssh-key-path)', default=PathTools.get_ssh_path())

        token = self._handle_token_and_data_path(force, org, token=token)

        if ssh_key_path is not None:
            ssh_key = self.export_key_from_path(ssh_key_path).decode('utf-8')

        prefix, ml_data = self.get_config_prefix_and_file(self.ctx.obj.config)

        self.setup_rms_volume(ssh_key=ssh_key, token=token, ml_data=ml_data, prefix=prefix, force=True, capacity=capacity, cache_path=cache_path)

    def _handle_token_and_data_path(self, force, org, token=None):
        cur_config = self.ctx.obj.config.resource_manager_config
        if force:
            click.echo('Current host config is deleted due to `--force` flag')
            cur_config = {}

        new_token = token or cur_config.get('token')

        if new_token is None:
            new_token = self.auth_resource(org)
        self.ctx.obj.config.update_and_save({
            'resource_manager': {
                'token': new_token,
            }
        })
        return new_token

    def _apply_ssh_params(self, ssh_key):
        if ssh_key is not None:
            return ['--ssh-private-key', ssh_key]

        return []

    def _apply_ws_server(self):
        if self.config.rm_socket_server:
            return ['--ml-server', self.config.rm_socket_server]

        return []

    def _apply_capacity(self, capacity):
        gpus = self.gpu_count()
        capacity_provided = capacity is None or capacity == 0
        if capacity_provided:
            return []

        if not gpus:
            capacity = 1
        else:
            if (gpus % capacity) != 0:
                raise click.BadParameter('The specified capacity %s is not a divisor of the number of GPUs detected %s' % (capacity, gpus))

        return ['--capacity', str(capacity)]

    def _ensure_auth(self):
        id_token = self.ctx.obj.config.id_token
        if id_token is None:
            raise click.UsageError('Please call `ml auth init` first')

    def _decode_if_needed(self, data):
        if data and isinstance(data, six.binary_type):
            return data.decode('utf-8')

        return data

    def _apply_ml_data(self, prefix, ml_data):
        if prefix is None and ml_data is None:
            self._ensure_auth()
            prefix, ml_data = self.get_config_prefix_and_file(self.ctx.obj.config)

        res = self._get_ml_data_param(ml_data)

        if prefix is not None:
            res.extend(['--ml-config-prefix', prefix])

        return res

    def _get_ml_data_param(self, ml_data):
        ml_data = self._decode_if_needed(ml_data)
        return ['--ml-config-file', ml_data]

    def _apply_token(self, token):
        if token is not None:
            return ['--ml-token', token]

        return []

    def _apply_backend(self):
        if self.config.ml_backend is not None:
            return ['--ml-backend', self.config.ml_backend]

        return []

    def append_cred_data_to_command(self, command):
        if self.cloud_credentials:
            self.cloud_credentials.extend_command_with_creds(command)

    def _apply_env(self, env):
        res = []
        if env is not None:
            for key, value in env.items():
                res += ['--env', key, value]
        return res

    def _apply_cache_path(self, cache_path):
        if cache_path is not None:
            return ['--cache-path', cache_path]

        return []

    def _apply_config_to_volume(self, ssh_key=None, token=None, prefix=None, ml_data=None, env=None, capacity=None, cache_path=None):
        conf_mounts = self.get_run_mounts()
        command = ['config']
        command.extend(self._apply_ws_server())
        command.extend(self._apply_backend())
        command.extend(self._apply_ssh_params(ssh_key))
        command.extend(self._apply_ml_data(prefix, ml_data))
        command.extend(self._apply_token(token))
        command.extend(self._apply_capacity(capacity))
        command.extend(self._apply_env(env))
        command.extend(self._apply_cache_path(cache_path))
        self.append_cred_data_to_command(command)
        cont = self.client.containers.run(
            self.config.rm_manager_image, command=command,
            volumes=conf_mounts,
            environment={'ML_RM_MANAGER': '1'}, detach=True)
        exit_code = cont.wait()
        if exit_code != 0:
            click.echo(cont.logs())
        cont.remove()

    def get_run_mounts(self):
        volumes = self._get_run_volumes()
        return self._get_combined_volume_path(*volumes)

    def _get_config_volume(self):
        return {self.config.rm_config_volume: {'bind': normalize_path('/config')}}

    def _get_run_volumes(self):
        return [self.ADMIN_VOLUME, self._get_config_volume()]

    def validate_config_volume(self):
        if not self.config_volume_if_present():
            raise click.BadArgumentUsage('Configuration volume is missing. Please re-install')

    def run_resource_manager(self, env=None):
        self.validate_config_volume()
        click.echo('Starting Resource Manager')
        run_mounts = self.get_run_mounts()
        environment = {'ML_RM_MANAGER': '1', 'ML_CONFIG_VOLUME': self.config.rm_config_volume}
        if env:
            environment.update(env)
        return self.client.containers.run(
            self.config.rm_manager_image,
            command=['run'],
            auto_remove=False,
            restart_policy={"Name": 'always'},
            volumes=run_mounts,
            environment=environment,
            detach=True,
            name=self.config.rm_container_name)

    def _volume_if_present(self, volume):
        return self._docker_present(self.client.volumes.get, volume)

    def config_volume_if_present(self):
        return self._volume_if_present(self.config.rm_config_volume)

    def ensure_cache_volume_present(self):
        cache_volume = '{}_cache'.format(self.config.rm_config_volume)
        if not self._docker_present(self.client.volumes.get, cache_volume):
            self.client.volumes.create(cache_volume)

        return cache_volume

    def resource_manager_server_container_if_present(self):
        return self._docker_present(self.client.containers.get, self.config.rm_container_name)

    def ensure_rms_volumes(self, force):
        self._ensure_config_volume(force)

    def _ensure_volume(self, volume, force):
        if self._volume_if_present(volume) and force:
            self.client.volumes.get(volume).remove(force=True)

        if not self._volume_if_present(volume):
            self.client.volumes.create(volume)

    def _ensure_config_volume(self, force):
        self._ensure_volume(self.config.rm_config_volume, force)

    def setup_rms_volume(self, ssh_key=None, token=None, prefix=None, ml_data=None, env=None, force=False, capacity=1, cache_path=None):
        click.echo('building volume')
        self.ensure_rms_volumes(force)
        self._apply_config_to_volume(ssh_key, token, prefix=prefix, ml_data=ml_data, env=env, capacity=capacity, cache_path=cache_path)

    def remove_current_rm_servers(self):
        click.echo('Clear containers')
        for container in self.client.containers.list():
            if container.name == self.config.rm_container_name:
                click.echo("\t  KILL: %s" % container.id)
                container.kill()
        click.echo('Remove containers')
        for container in self.client.containers.list():
            if container.name == self.config.rm_container_name:
                container.remove(force=True)

    def _get_gpus(self):
        logger.debug('Validating GPU...')
        self.pull_image(self.CUDA_BASE_IAMGE, 'Validating GPU configuration')
        smi_output = self.client.containers.run(
            self.CUDA_BASE_IAMGE, 'nvidia-smi  --query-gpu=index  --format=csv,noheader,nounits',
            runtime="nvidia", remove=True)
        gpus = len(smi_output.decode('utf-8').strip().split('\n'))
        return gpus

    def gpu_count(self):
        try:
            return self._get_gpus()
        except Exception as ex:
            logger.debug('GPU not found, ignore the error if you do not have GPU installed on this machine', exc_info=1)
            logger.info('GPU not found, ignore the error if you do not have GPU installed on this machine: %s', str(ex))
            return 0

    def _extract_container_display(self, container):
        if container.name == self.config.rm_container_name:
            return 'Resource manager'

        res = []
        if 'ML_JOB_ID' in container.labels:
            res.append(container.labels['ML_JOB_ID'])
        if 'ML_STAGE_NAME' in container.labels:
            res.append(container.labels['ML_STAGE_NAME'])

        return ': '.join(res)

    def running_ml_containers(self):
        return [
            running_ml_container(container.short_id, container.name, self._extract_container_display(container), container)
            for container in self.client.containers.list()
            if container.name == self.config.rm_container_name or 'ML' in container.labels
        ]
