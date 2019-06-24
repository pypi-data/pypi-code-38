import os
from .openbis_command import OpenbisCommand
from ..command_result import CommandResult, CommandException
from ..utils import complete_openbis_config


class Addref(OpenbisCommand):
    """
    Command to add the current folder, which is supposed to be an obis repository, as 
    a new content copy to openBIS.
    """

    def __init__(self, dm):
        super(Addref, self).__init__(dm)


    def run(self):
        self.update_external_dms_id()
        result = self.check_obis_repository()
        if result.failure():
            return result
        self.openbis.new_content_copy(self.path(), self.commit_id(), self.repository_id(), self.external_dms_id(), self.data_set_id())
        return CommandResult(returncode=0, output="")


    def update_external_dms_id(self):
        self.set_external_dms_id(None)
        self.prepare_external_dms()


    def check_obis_repository(self):
        if os.path.exists('.obis'):
            return CommandResult(returncode=0, output="")
        else:
            return CommandResult(returncode=-1, output="This is not an obis repository.")


    def commit_id(self):
        result = self.git_wrapper.git_commit_hash()
        if result.failure():
            return result
        return result.output
