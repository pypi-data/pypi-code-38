import sys
import subprocess
import socket
import os

from os import path

from cpbox.tool import utils
from cpbox.tool import system
from cpbox.tool import file
from cpbox.tool import logger
from cpbox.tool import template
from cpbox.tool import array

from cpbox.tool import functocli
from cpbox.app.appconfig import appconfig


class DevOpsAppConfig:

    def __init__(self, app_name, provider):
        appconfig.init(app_name, provider.get_env(), provider.get_config())

        self.app_name = app_name
        self.env = provider.get_env()
        self.root_dir = provider.get_root_dir()
        self.roles_dir = self.root_dir + '/roles'

        app_root_dir = provider.get_app_root_dir()
        self.app_root_dir = app_root_dir

        self.app_config_dir = app_root_dir + '/config'
        self.app_templates_dir = app_root_dir + '/templates'
        self.app_scripts_dir = app_root_dir + '/scripts'

        self.app_storage_dir = '/opt/data/' + app_name
        self.app_persitent_storage_dir = self.app_storage_dir + '/persistent'
        self.app_persistent_storage_dir = self.app_storage_dir + '/persistent'
        self.app_runtime_storage_dir = self.app_storage_dir + '/runtime'
        self.app_logs_dir = self.app_runtime_storage_dir + '/logs'

        self.ensure_dir_and_write_permission()

    def ensure_dir_and_write_permission(self):
        file.ensure_dir(self.app_storage_dir)
        file.ensure_dir(self.app_persistent_storage_dir)
        file.ensure_dir(self.app_runtime_storage_dir)
        file.ensure_dir(self.app_logs_dir)
        file.ensure_dir(self.app_logs_dir + '/syslog')


class DevOpsAppConfigProvider:

    def __init__(self, app_name):
        self.app_name = app_name
        import __main__ as main
        self.is_interactive = hasattr(main, '__file__')

    def get_root_dir(self):
        if self.is_interactive:
            root_dir = path.dirname(path.realpath(sys.argv[0]))
            return root_dir
        else:
            root_dir = os.getcwd()
            return root_dir

    def get_app_root_dir(self):
        app_root_dir = self.get_root_dir() + '/roles/' + self.app_name
        return app_root_dir

    def get_env(self):
        env = os.environ['PUPPY_ENV'] if 'PUPPY_ENV' in os.environ else 'dev'
        return env

    def get_config(self):
        return {}


class DevOpsApp(object):

    def _want_logger_ex(self):
        logger.make_logger_for_app(self)
        return logger.getLogger(self.app_name)

    def __init__(self, app_name, log_level='info', exit_on_error=True, **kwargs):
        self.app_name = app_name
        self.app_config_provider = self.create_app_config_provider()
        self.app_config = DevOpsAppConfig(app_name, self.app_config_provider)

        self._inject_app_config()

        self.log_level = log_level
        self.exit_on_error = exit_on_error
        self.logger = self._want_logger_ex()

        hostname = socket.gethostname()
        self.hostname_fqdn = hostname
        self.hostname_short = hostname.split('.', 1)[0]

        self.file_lock = None
        self._hostvar = None

    def _inject_app_config(self):

        attrs = [
            'env',
            'root_dir',
            'roles_dir',
            'app_root_dir',
            'app_config_dir',
            'app_templates_dir',
            'app_scripts_dir',
            'app_storage_dir',
            'app_persitent_storage_dir',
            'app_persistent_storage_dir',
            'app_runtime_storage_dir',
            'app_logs_dir',
        ]

        for attr in attrs:
            setattr(self, attr, getattr(self.app_config, attr))

    def create_app_config_provider(self):
        return DevOpsAppConfigProvider(self.app_name)

    def run_cmd_ret(self, cmd, log=True):
        return self.run_cmd(cmd, log=log)[1]

    def run_cmd(self, cmd, log=True):
        if log:
            self.logger.info('run_cmd: %s', cmd)
        return system.run_cmd(cmd)

    def shell_run(self, cmd, keep_pipeline=True, exit_on_error=True, dry_run=False):
        self.logger.info('shell_run: %s', cmd)
        if dry_run:
            return 0
        exit_on_error = exit_on_error and self.exit_on_error
        return system.shell_run(cmd, keep_pipeline=keep_pipeline, exit_on_error=exit_on_error)

    def remove_container(self, name, force=False, dry_run=False):
        cmd = 'docker rm %s' % (name)
        if force:
            cmd = 'docker rm -f %s' % (name)
        self.shell_run(cmd, exit_on_error=False, dry_run=dry_run)

    def container_is_running(self, name):
        cmd = 'docker ps | grep %s' % (name)
        return self.run_cmd(cmd, log=False)[0] == 0

    def stop_container(self, name, timeout=300, dry_run=False):
        cmd = 'docker stop --time %d %s' % (timeout, name)
        self.shell_run(cmd, exit_on_error=False, dry_run=dry_run)

    def _check_lock(self):
        filepath = self.app_runtime_storage_dir + '/locks/' + file.compute_lock_filepath(sys.argv)
        file_lock = file.obtain_lock(filepath)
        if file_lock is None:
            pid = 0
            with open(filepath, 'r') as f:
                pid = f.read()
            self.logger.warning('lock file exists, pid: %s => %s', pid, filepath)
            sys.exit(1)
        else:
            self.file_lock = file_lock

    def template_to(self, template_filename, dst, payload, app_name=None):
        template_payload = {'payload': payload}
        src = self.app_templates_dir_for(app_name) + '/' + template_filename
        template.render_to_file(src, template_payload, dst)
        self.logger.info('template_to: %s => %s', src, dst)

    def read_app_config(self, config_filebasename, app_name=None):
        if '.yml' not in config_filebasename:
            config_filebasename = config_filebasename + '.yml'
        data = utils.load_yaml('%s/%s' % (self.app_config_dir_for(app_name), config_filebasename), {})
        return data

    def app_templates_dir_for(self, app_name=None):
        if app_name is None:
            return self.app_templates_dir
        return '%s/%s/templates' % (self.roles_dir, app_name)

    def app_config_dir_for(self, app_name=None):
        if app_name is None:
            return self.app_config_dir
        return '%s/%s/config' % (self.roles_dir, app_name)

    def get_group_names(self):
        return self._get_hostvar()['group_names']

    def get_configed_ops_scripts_dir(self):
        return self._get_hostvar()['ops_scripts_dir']

    def _get_hostvar(self):
        if self._hostvar is None:
            ansible_kv_config = utils.load_json('/etc/cp-ansible-hostvar.json', {})
            cloud_init_raw_data = utils.load_json('/etc/cp-cloud-init-raw-data.json', {})
            '''
            #### Always respect global_params / app_params from ansible
            1. Create an ECS by cloud-init, global_params from ansible, app_params from cloud-init config.
               We can not read app_params from ansible when we are using cloud-init to deloy,
               so we truncate `/etc/cp-ansible-hostvar.json` when lauch an ECS.
               The global_params and app_params will be the value we desire.
            2. If we deploy by ansible, ansible_kv_config will overwrite cloud_init_raw_data,
               so global_params and app_params both will be the latest. So they are the value we desire too.
            '''
            self._hostvar = array.merge(cloud_init_raw_data, ansible_kv_config)
        return self._hostvar

    def get_app_params(self, key=None, fallback=None):
        app_params = self._get_hostvar().get('app_params', {})
        if key is None:
            return app_params
        return app_params.get(key, fallback)

    def get_global_params(self, key=None, fallback=None):
        global_params = self._get_hostvar().get('global_params', {})
        if key is None:
            return global_params
        return global_params.get(key, fallback)

    @functocli.keep_method
    def check_health(self):
        print('%s is good' % (sys.argv[0]))
