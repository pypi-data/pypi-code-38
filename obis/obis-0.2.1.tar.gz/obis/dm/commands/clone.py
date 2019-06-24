import os
import pybis
from .openbis_command import OpenbisCommand, ContentCopySelector
from ..checksum import validate_checksum
from ..command_result import CommandResult, CommandException
from ..utils import cd
from ..utils import run_shell
from ..utils import complete_openbis_config
from ..repository_utils import copy_repository
from ... import dm


class Clone(OpenbisCommand):
    """
    Implements the clone command. Copies a repository from a content copy of a data set
    and adds the local copy as a new content copy using the addref command.
    Validates the checksums of the copied files unless skip_integrity_check is True.
    """

    def __init__(self, dm, data_set_id, ssh_user, content_copy_index, skip_integrity_check):
        """
        :param dm: data management
        :param data_set_id: permId of the data set to be cloned
        :param ssh_user: user for remote access
        :param content_copy_index: in case of multiple content copied
        :param skip_integrity_check: Checksums are not validated if True
        """
        if dm.data_path != dm.metadata_path:
            raise CommandException(CommandResult(returncode=-1, output='Clone/move not supported with obis_metadata_folder.'))
        self.data_set_id = data_set_id
        self.ssh_user = ssh_user
        self.content_copy_index = content_copy_index
        self.skip_integrity_check = skip_integrity_check
        self.load_global_config(dm)
        super(Clone, self).__init__(dm)


    def check_configuration(self):
        missing_config_settings = []
        if self.openbis is None:
            missing_config_settings.append('openbis_url')
        if self.user() is None:
            missing_config_settings.append('user')
        if len(missing_config_settings) > 0:
            return CommandResult(returncode=-1,
                                 output="Missing configuration settings for {}.".format(missing_config_settings))
        return CommandResult(returncode=0, output="")


    def run(self):

        result = self.prepare_run()
        if result.failure():
            return result

        data_set = self.openbis.get_dataset(self.data_set_id)

        content_copy = ContentCopySelector(data_set, self.content_copy_index).select()
        self.content_copy = content_copy
        host = content_copy['externalDms']['address'].split(':')[0]
        path = content_copy['path']
        repository_folder = path.split('/')[-1]

        result = copy_repository(self.ssh_user, host, path)
        if result.failure():
            return result
        result = self.checkout_commit(content_copy, path)
        if result.failure():
            return result
        data_set = self.openbis.get_dataset(self.data_set_id)
        if self.skip_integrity_check != True:
            data_path = os.path.join(self.data_mgmt.data_path, repository_folder)
            invalid_files = validate_checksum(self.openbis, data_set.file_list, data_set.permId, data_path, self.data_mgmt.metadata_path)
            if len(invalid_files) > 0:
                raise CommandException(CommandResult(returncode=-1, output="Invalid checksum for files {}.".format(str(invalid_files))))
        return self.add_content_copy_to_openbis(repository_folder)


    def checkout_commit(self, content_copy, path):
        """
        Checks out the commit of the content copy from which the clone was made 
        in case there are newer commits / data sets. So the new copy is based on the 
        data set given as an input.
        """
        commit_hash = content_copy['gitCommitHash']
        repository_folder = path.split('/')[-1]
        return self.git_wrapper.git_checkout(commit_hash, relative_repo_path=repository_folder)


    def add_content_copy_to_openbis(self, repository_folder):
        with cd(repository_folder):
            data_path = os.path.join(self.data_mgmt.data_path, repository_folder)
            metadata_path = os.path.join(self.data_mgmt.metadata_path, repository_folder)
            invocation_path = self.data_mgmt.invocation_path
            data_mgmt = dm.DataMgmt(openbis_config={}, git_config={
                    'find_git': True,
                    'data_path': data_path,
                    'metadata_path': metadata_path,
                    'invocation_path': invocation_path
                })
            data_mgmt.set_property(data_mgmt.settings_resolver.config, 'hostname', None, False)
            return data_mgmt.addref()
