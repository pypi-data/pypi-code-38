import json
import os
from .openbis_command import OpenbisCommand, ContentCopySelector
from ..command_result import CommandResult, CommandException
from ..utils import complete_openbis_config


class Removeref(OpenbisCommand):
    """
    Command to remove the content copy corresponding to the
    obis repository from openBIS.
    """

    def __init__(self, dm, data_set_id=None):
        self._data_set_id = data_set_id
        self.load_global_config(dm)
        super(Removeref, self).__init__(dm)


    def run(self):

        if self._data_set_id is None:
            self._remove_content_copies_from_repository()
        else:
            self._remove_content_copies_from_data_set()


        return CommandResult(returncode=0, output="")


    def _remove_content_copies_from_repository(self):
        result = self.check_obis_repository()
        if result.failure():
            raise CommandException(result)

        data_set = self.openbis.get_dataset(self.data_set_id())
        self._validate_data_set(data_set)

        content_copies = data_set.data['linkedData']['contentCopies']
        content_copies_to_delete = list(filter(lambda cc: 
                cc['externalDms']['code'] == self.external_dms_id() and cc['path'] == self.path()
            , content_copies))

        if len(content_copies_to_delete) == 0:
            raise CommandException(CommandResult(returncode=-1, output="Matching content copy not fount in data set: " + self.data_set_id()))

        for content_copy in content_copies_to_delete:
            self.openbis.delete_content_copy(self.data_set_id(), content_copy)


    def _remove_content_copies_from_data_set(self):
        data_set = self.openbis.get_dataset(self._data_set_id)
        self._validate_data_set(data_set)
        selector = ContentCopySelector(data_set)
        content_copy_to_delete = selector.select()
        self.openbis.delete_content_copy(self._data_set_id, content_copy_to_delete)


    def _validate_data_set(self, data_set):
        if data_set.data['linkedData'] is None:
            raise CommandException(CommandResult(returncode=-1, output="Data set has no linked data: " + self.data_set_id()))

        if data_set.data['linkedData']['contentCopies'] is None:
            raise CommandException(CommandResult(returncode=-1, output="Data set has no content copies: " + self.data_set_id()))


    def check_obis_repository(self):
        if os.path.exists('.obis'):
            return CommandResult(returncode=0, output="")
        else:
            return CommandResult(returncode=-1, output="This is not an obis repository.")


    def path(self):
        result = self.git_wrapper.git_top_level_path()
        if result.failure():
            return result
        return result.output


    def commit_id(self):
        result = self.git_wrapper.git_commit_hash()
        if result.failure():
            return result
        return result.output
