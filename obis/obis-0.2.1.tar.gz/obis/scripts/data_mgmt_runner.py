import click
import json
import os
import sys

from datetime import datetime

from .. import dm
from ..dm.utils import cd
from ..dm.command_result import CommandResult, CommandException
from ..dm.command_log import CommandLog
from ..dm.utils import run_shell
from .click_util import click_echo, check_result


class DataMgmtRunner(object):


    def __init__(self, context, halt_on_error_log=True, data_path=None, bootstrap_settings=None, check_result=True, login=True, openbis=None):
        self.context = context
        self.halt_on_error_log = halt_on_error_log
        self.data_path = data_path
        self.metadata_path = None
        self.invocation_path = os.getcwd()
        self.bootstrap_settings = bootstrap_settings
        self.check_result = check_result
        self.login = login
        self.openbis = openbis


    def init_paths(self, repository=None):
        # data path
        if self.data_path is None:
            self.data_path = run_shell(['pwd'], raise_exception_on_failure=True).output
            if repository is not None:
                self.data_path = os.path.join(self.data_path, repository)
        # metadata path
        if self.metadata_path is None:
            self.metadata_path = self.data_path
            obis_metadata_folder = self.get_settings().get('config').get('obis_metadata_folder')
            if obis_metadata_folder is not None:
                result = self._validate_obis_metadata_folder(obis_metadata_folder)
                if result.failure():
                    click_echo(result.output)
                else:
                    self.metadata_path = os.path.join(obis_metadata_folder, self.data_path[1:])
        if not os.path.exists(self.metadata_path):
            os.makedirs(self.metadata_path)
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)


    def _validate_obis_metadata_folder(self, obis_metadata_folder):
        if not os.path.isabs(obis_metadata_folder):
            return CommandResult(
                returncode=-1, 
                output="Ignoring obis_metadata_folder. Must be absolute but is: {}".format(obis_metadata_folder))
        if not os.path.exists(obis_metadata_folder):
            return CommandResult(
                returncode=-1, 
                output="Ignoring obis_metadata_folder. Folder does not exist: {}".format(obis_metadata_folder))
        return CommandResult(returncode=0, output="")


    def run(self, command, function, repository=None):
        self.init_paths(repository)
        with cd(self.metadata_path):
            result = self._run(function)
        if self.check_result:
            return check_result(command, result)
        else:
            return result


    def _run(self, function):
        try:
            dm = self._get_dm()
            if self.bootstrap_settings is not None:
                dm.setup_local_settings(self.bootstrap_settings)
            return function(dm)
        except CommandException as e:
            return e.command_result
        except Exception as e:
            if self.context['debug'] == True:
                raise e
            return CommandResult(returncode=-1, output="Error: " + str(e))


    def get_settings(self, repository=None, do_cd=True):
        self.init_paths()
        with cd(self.metadata_path):
            return self.get_settings_resolver(do_cd).config_dict()


    def get_settings_resolver(self, do_cd=True):
        if do_cd:
            self.init_paths()
            with cd(self.metadata_path):
                return self._get_dm().get_settings_resolver()
        else:
            return self._get_dm().get_settings_resolver()


    def config(self, resolver, is_global, is_data_set_property, prop, value, set, get, clear):
        self.init_paths()
        with cd(self.metadata_path):
            self._get_dm().config(resolver, is_global, is_data_set_property, prop, value, set, get, clear)


    def _get_dm(self):
        git_config = {
                'find_git': True,
                'data_path': self.data_path,
                'metadata_path': self.metadata_path,
                'invocation_path': self.invocation_path
            }
        openbis_config = {}
        if self.context.get('verify_certificates') is not None:
            openbis_config['verify_certificates'] = self.context['verify_certificates']
        log = CommandLog()
        if self.halt_on_error_log and log.any_log_exists():
            click_echo("Error: A previous command did not finish. Please check the log ({}) and remove it when you want to continue using obis".format(log.folder_path))
            sys.exit(-1)
        return dm.DataMgmt(openbis_config=openbis_config, git_config=git_config, log=log, debug=self.context['debug'], login=self.login, openbis=self.openbis)
