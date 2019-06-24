import pybis
from ..command_result import CommandResult
import uuid
import os
from ..git import GitRepoFileInfo
from .openbis_command import OpenbisCommand


class OpenbisSync(OpenbisCommand):
    """A command object for synchronizing with openBIS.
    1) Checks that the previous data set exists.
    2) Does nothing if the current git hash is already tracked in openBIS.
    3) Ensures the repository id.
    4) Ensures the external data management system.
    5) Creates the data set in openBIS.
    6) Updates the obis metadata.
    """


    def __init__(self, dm, ignore_missing_parent=False):
        """
        :param ignore_missing_parent: Normally, there is an error if the data_set_id 
            of the repository doesn't exist. If this flag is true, this error is ignored 
            and the a new data set can be created.
        """
        self.ignore_missing_parent = ignore_missing_parent
        super(OpenbisSync, self).__init__(dm)


    def check_configuration(self):
        missing_config_settings = []
        if self.openbis is None:
            missing_config_settings.append('openbis_url')
        if self.user() is None:
            missing_config_settings.append('user')
        if self.data_set_type() is None:
            missing_config_settings.append('data_set type')
        if self.object_id() is None and self.object_permId() is None and self.collection_id() is None and self.collection_permId() is None:
            missing_config_settings.append('object id or collection id')
        if len(missing_config_settings) > 0:
            return CommandResult(returncode=-1,
                                 output="Missing configuration settings for {}.".format(missing_config_settings))
        return CommandResult(returncode=0, output="")


    def create_data_set_code(self):
        try:
            data_set_code = self.openbis.create_permId()
            return CommandResult(returncode=0, output=""), data_set_code
        except Exception as e:
            return CommandResult(returncode=-1, output=str(e)), None

    def create_data_set(self, data_set_code, external_dms, repository_id, ignore_parent=False):
        data_set_type = self.data_set_type()
        parent_data_set_id = None if ignore_parent else self.data_set_id()
        properties = self.data_set_properties()
        result = self.git_wrapper.git_top_level_path()
        if result.failure():
            return result
        top_level_path = result.output
        result = self.git_wrapper.git_commit_hash()
        if result.failure():
            return result
        commit_id = result.output
        sample_id, experiment_id = self._update_and_get_object_or_collection_id()
        contents = GitRepoFileInfo(self.git_wrapper).contents(git_annex_hash_as_checksum=self.git_annex_hash_as_checksum())
        try:
            data_set = self.openbis.new_git_data_set(data_set_type, top_level_path, commit_id, repository_id, external_dms.code,
                                                     sample=sample_id, experiment=experiment_id, properties=properties, parents=parent_data_set_id,
                                                     data_set_code=data_set_code, contents=contents)
            return CommandResult(returncode=0, output="Created data set {}.".format(str(data_set))), data_set
        except Exception as e:
            return CommandResult(returncode=-1, output=str(e)), None


    def _update_and_get_object_or_collection_id(self):
        """ Updates identifier of object / collection in case it has changed in openBIS 
        if the permId is available. Returns sample / experiment identifier."""
        sample_id = self.object_id()
        experiment_id = self.collection_id()
        if self.object_permId() is not None:
            sample_id = self.openbis.get_sample(self.object_permId()).identifier
            if sample_id != self.object_id():
                self.settings_resolver.object.set_value_for_parameter('id', sample_id, 'local')
                # permId is cleared when the id is set - set it again
                self.settings_resolver.object.set_value_for_parameter('permId', self.object_permId(), 'local')
        if self.collection_permId() is not None:
            experiment_id = self.openbis.get_experiment(self.collection_permId()).identifier
            if experiment_id != self.collection_id():
                self.settings_resolver.collection.set_value_for_parameter('id', experiment_id, 'local')
                # permId is cleared when the id is set - set it again
                self.settings_resolver.collection.set_value_for_parameter('permId', self.collection_permId(), 'local')
        return sample_id, experiment_id

    def _storePermId(self):
        if self.object_permId() is None and self.object_id() is not None:
            sample = self.openbis.get_sample(self.object_id())
            self.settings_resolver.object.set_value_for_parameter('permId', sample.permId, 'local')
        if self.collection_permId() is None and self.collection_id() is not None:
            experiment = self.openbis.get_experiment(self.collection_id())
            self.settings_resolver.collection.set_value_for_parameter('permId', experiment.permId, 'local')


    def prepare_repository_id(self):
        repository_id = self.repository_id()
        if self.repository_id() is None:
            repository_id = str(uuid.uuid4())
            self.settings_resolver.repository.set_value_for_parameter('id', repository_id, 'local')
        return CommandResult(returncode=0, output=repository_id)


    def handle_unsynced_commits(self):
        return CommandResult(returncode=0, output="")


    def handle_missing_data_set(self):
        return CommandResult(returncode=0, output="")


    def git_hash_matches(self, data_set):
        content_copies = data_set.data['linkedData']['contentCopies']
        for content_copy in content_copies:
            cc_commit_hash = content_copy['gitCommitHash']
            result = self.git_wrapper.git_commit_hash()
            if result.failure():
                return result
            git_comit_hash = result.output
            if cc_commit_hash == git_comit_hash:
                return True
        return False

    def continue_without_parent_data_set(self):

        if self.ignore_missing_parent:
            return True

        while True:
            print("The data set {} not found in openBIS".format(self.data_set_id()))
            print("Create new data set without parent? (y/n)")
            continue_without_parent = input("> ")
            if continue_without_parent == "y":
                return True
            elif continue_without_parent == "n":
                return False 


    def run(self, info_only=False):
        """
        :param info_only: If true, nothing is actually synced. We only get the info 
            whether or not a sync is needed.
        """

        ignore_parent = False

        if self.data_set_id() is not None:
            try:
                data_set = self.openbis.get_dataset(self.data_set_id())
                if self.git_hash_matches(data_set):
                    return CommandResult(returncode=0, output="Nothing to sync.")
            except Exception as e:
                if 'no such dataset' in str(e):
                    if info_only:
                        return CommandResult(returncode=-1, output="Parent data set not found in openBIS.")
                    ignore_parent = self.continue_without_parent_data_set()
                    if not ignore_parent:
                        return CommandResult(returncode=-1, output="Parent data set not found in openBIS.")
                else:
                    raise e

        if info_only:
            if self.data_set_id() is None:
                return CommandResult(returncode=-1, output="Not yet synchronized with openBIS.")
            else:
                return CommandResult(returncode=-1, output="There are git commits which have not been synchronized.")

        # TODO Write mementos in case openBIS is unreachable
        # - write a file to the .git/obis folder containing the commit id. Filename includes a timestamp so they can be sorted.

        result = self.prepare_run()
        if result.failure():
            return result

        result = self.prepare_repository_id()
        if result.failure():
            return result
        repository_id = result.output

        result = self.prepare_external_dms()
        if result.failure():
            return result
        external_dms = result.output

        result, data_set_code = self.create_data_set_code()
        if result.failure():
            return result

        # store permId of object / collection so we can use those as a reference in the future
        self._storePermId()

        self.settings_resolver.repository.set_value_for_parameter('data_set_id', data_set_code, 'local')

        # create a data set, using the existing data set as a parent, if there is one
        result, data_set = self.create_data_set(data_set_code, external_dms, repository_id, ignore_parent)

        return result
