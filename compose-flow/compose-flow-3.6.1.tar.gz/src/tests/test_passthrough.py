from compose_flow.commands.subcommands.passthrough_base import PassthroughBaseSubcommand
from tests import BaseTestCase, mock


class TestPassthroughSubcommand(PassthroughBaseSubcommand):
    def fill_subparser(self, cls, parser):
        pass


class BaseSubcommandTestCase(BaseTestCase):
    @mock.patch('compose_flow.commands.subcommands.passthrough_base.os')
    def test_execute(self, *mocks):
        workflow = mock.Mock()

        command = TestPassthroughSubcommand(workflow)
        proc = command.execute('docker ps')

        # make sure that sh was executed with the workflow environment
        sh_mock = self.sh_mock
        sh_mock.docker.assert_called_with('ps', _env=workflow.environment.data.copy())
