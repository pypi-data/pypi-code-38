import shlex

from unittest import mock

from compose_flow.commands import Workflow

from tests import BaseTestCase


@mock.patch('compose_flow.commands.subcommands.env.get_backend')
@mock.patch('compose_flow.commands.subcommands.env.os')
@mock.patch('compose_flow.commands.subcommands.profile.Profile.write')
class TaskTestCase(BaseTestCase):
    @mock.patch('compose_flow.commands.subcommands.env.Env.rw_env', new=True)
    @mock.patch('compose_flow.commands.subcommands.env.utils')
    def test_config_updated(self, *mocks):
        """
        Ensures that the config is updated in order to run tasks on the latest locally built image
        """
        utils_mock = mocks[0]
        utils_mock.get_tag_version.return_value = '0.0.1-test'
        utils_mock.render.side_effect = lambda x, **kwargs: x

        command = shlex.split('-e test task foo')
        workflow = Workflow(argv=command)

        self.assertEqual(True, 'DOCKER_IMAGE' in workflow.environment.data)
