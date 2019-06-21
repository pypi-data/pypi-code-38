from compose_flow.commands.subcommands.base import BaseSubcommand
from tests import BaseTestCase, mock


class TestSubcommand(BaseSubcommand):
    def fill_subparser(self, cls, parser):
        pass


class BaseSubcommandTestCase(BaseTestCase):
    @mock.patch('compose_flow.shell.OS_ENV_INCLUDES', new_callable=dict)
    def test_execute(self, *mocks):
        workflow = mock.Mock()
        workflow.environment.data = {}

        command = TestSubcommand(workflow)
        proc = command.execute('docker ps')

        # make sure that sh was executed with the workflow environment
        sh_mock = self.sh_mock
        sh_mock.docker.assert_called_with('ps', _env=workflow.environment.data)
