import os
import sys
import getpass
import socket

from os import path

from cpbox.tool import functocli
from cpbox.tool import template
from cpbox.tool import net
from cpbox.tool import utils
from cpbox.tool import file
from cpbox.app.devops import DevOpsApp
from cpbox.app.devops import DevOpsAppConfigProvider

class SimpleMultiDeveloperDevOpsAppConfigProvider(DevOpsAppConfigProvider):

    def __init__(self, app, app_base_name, kwargs):
        self.app = app
        self.app_base_name = app_base_name
        self.kwargs = kwargs
        self.determine_developer_name()
        app_name = self.determine_app_name()
        DevOpsAppConfigProvider.__init__(self, app_name)

    def determine_developer_name(self):
        developer_name = os.environ['PUPPY_DEVELOPER_NAME'] if 'PUPPY_DEVELOPER_NAME' in os.environ else getpass.getuser()
        developer_name_from_cmd = self.kwargs.get('developer_name', None)
        self.developer_name = developer_name_from_cmd if developer_name_from_cmd else developer_name

    def determine_app_name(self):
        if self.app.isolate_by_developer():
            env = self.get_env()
            app_name = '%s-%s-%s' % (env, self.developer_name, self.app_base_name)
            return app_name
        else:
            return self.app_base_name

    def get_app_root_dir(self):
        app_root_dir = self.get_root_dir() + '/roles/' + self.app_base_name
        return app_root_dir

    def get_env(self):
        env_from_puppy_env = DevOpsAppConfigProvider.get_env(self)
        env_from_cmd_args = self.kwargs.get('env')
        return env_from_cmd_args if env_from_cmd_args else env_from_puppy_env

    def get_config(self):
        return {}

class MultiDeveloperDevOpsAppConfigProvider(SimpleMultiDeveloperDevOpsAppConfigProvider):

    def __init__(self, app, app_base_name, kwargs):
        SimpleMultiDeveloperDevOpsAppConfigProvider.__init__(self, app, app_base_name, kwargs)

    def determine_app_name(self):
        env = self.get_env()
        if env == 'test' or env == 'dev':
            self.sandbox_version = self.kwargs.get('sandbox_version', 0)
        else:
            self.sandbox_version = 0

        self.shadow_id = int(os.getenv('shadow_id', 0))

        app_name = '%s-%s-%s' % (env, self.developer_name, self.app_base_name)
        if self.sandbox_version != 0:
            app_name = '%s-%s-%s-sandbox-%s' % (env, self.developer_name, self.app_base_name, self.sandbox_version)

        if self.shadow_id != 0:
            app_name = '%s-%s-%s-shadow-%s' % (env, self.developer_name, self.app_base_name, self.shadow_id)
        return app_name

class SimpleMultiDeveloperDevOpsApp(DevOpsApp):

    def __init__(self, app_base_name, *args, **kwargs):
        self.app_base_name = app_base_name
        self.kwargs = kwargs
        self.app_config_provider = SimpleMultiDeveloperDevOpsAppConfigProvider(self, self.app_base_name, self.kwargs)
        self.developer_name = self.app_config_provider.developer_name

        DevOpsApp.__init__(self, self.app_config_provider.app_name, **kwargs)

    def create_app_config_provider(self):
        return self.app_config_provider

    def isolate_by_developer(self):
        return False

    @staticmethod
    def run_app(app, log_level='info', default_method=None, common_args_option=None):
        common_args_option_basic = {
                'args': ['env', 'developer_name'],
                'default_values': {
                    'env': None,
                    'developer_name': None,
                    }
                }
        functocli.run_app(app, log_level, default_method, common_args_option, common_args_option_basic)

class MultiDeveloperDevOpsApp(DevOpsApp):

    def __init__(self, app_base_name, *args, **kwargs):
        self.app_base_name = app_base_name
        self.kwargs = kwargs
        self.app_config_provider = MultiDeveloperDevOpsAppConfigProvider(self, self.app_base_name, self.kwargs)
        self.developer_name = self.app_config_provider.developer_name

        DevOpsApp.__init__(self, self.app_config_provider.app_name, **kwargs)

        self.shadow_id = self.app_config_provider.shadow_id
        self.sandbox_version = self.app_config_provider.sandbox_version

        if self.is_dev():
            self._prepare_config_for_dev()
        else:
            self._prepare_config_for_none_dev()

    def isolate_by_developer(self):
        return True

    def create_app_config_provider(self):
        return self.app_config_provider

    def is_dev(self):
        env = self.app_config_provider.get_env()
        return env == 'dev' or env == 'test'

    def _prepare_config_for_none_dev(self):
        data = utils.load_yaml(self.app_config_dir + '/env-config.yml')
        self.env_config = data[self.env]
        self.app_init_config_by_developer_name()
        self.app_do_init_for_deploy()

    def _prepare_config_for_dev(self):
        self.dev_env_config_file = self.app_persitent_storage_dir + '/dev-env-config.yml'
        if not os.path.isfile(self.dev_env_config_file) or self.shadow_id:
            self.do_init_for_dev()
        else:
            self.env_config = utils.load_yaml(self.dev_env_config_file)
            self.app_init_config_by_developer_name()

    def check_out_for_sandbox(self):
        sandbox_code_dir = self.app_persitent_storage_dir + '/sandbox-code-' + str(self.sandbox_version)
        file.ensure_dir(sandbox_code_dir)
        cmd = "cp -r %s/* %s" % (self.root_dir, sandbox_code_dir)
        self.shell_run(cmd)

    @functocli.keep_method
    def do_init_for_dev(self):
        self.app_config.ensure_dir_and_write_permision()
        config = self.app_build_env_config()
        utils.dump_yaml(self.dev_env_config_file, config)
        self.logger.info('generate dev env config: %s', self.dev_env_config_file)

        self.env_config = config

        if self.sandbox_version:
            self.check_out_for_sandbox()

        self.app_init_config_by_developer_name()

        self.app_do_init_for_dev()

    def app_init_config_by_developer_name(self):
        raise NotImplementedError("Please implement this method")

    def app_do_init_for_deploy(self):
        raise NotImplementedError("Please implement this method")

    def app_do_init_for_dev(self):
        raise NotImplementedError("Please implement this method")

    def app_build_env_config(self):
        raise NotImplementedError("Please implement this method")

    @staticmethod
    def run_app(app, log_level='info', default_method=None, common_args_option=None):
        common_args_option_basic = {
                'args': ['env', 'sandbox_version', 'developer_name'],
                'default_values': {
                    'env': None,
                    'sandbox_version': 0,
                    'developer_name': None,
                    }
                }
        functocli.run_app(app, log_level, default_method, common_args_option, common_args_option_basic)
