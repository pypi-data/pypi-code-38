import shlex

from unittest import mock

from compose_flow import utils
from compose_flow.commands import Workflow

from tests import BaseTestCase


@mock.patch('compose_flow.commands.workflow.PROJECT_NAME', new='testdirname')
class PublishTestCase(BaseTestCase):
    @mock.patch('compose_flow.commands.subcommands.env.utils')
    @mock.patch('compose_flow.commands.subcommands.env.get_backend')
    def test_profile_env(self, *mocks):
        """
        Ensure the VERSION is updated
        """
        utils_mock = mocks[1]
        utils_mock.get_tag_version.return_value = '0.0.1'
        utils_mock.render = utils.render

        command = shlex.split('-e dev publish')
        flow = Workflow(argv=command)

        flow.subcommand.build = mock.Mock()
        flow.subcommand.push = mock.Mock()

        flow.run()

        env_data = flow.environment.data

        self.assertEqual(True, 'VERSION' in env_data)

    def test_publish_with_missing_env_vars(self, *mocks):
        command = shlex.split('publish')
        flow = Workflow(argv=command)

        flow.subcommand.build = mock.Mock()
        flow.subcommand.check = mock.Mock()
        flow.subcommand.push = mock.Mock()

        with mock.patch(
            'compose_flow.commands.workflow.Workflow.profile',
            new_callable=mock.PropertyMock,
        ) as profile_mock:
            flow.run()

            profile_mock.return_value.write.assert_called_with()

        flow.subcommand.push.assert_called()

        # make sure check is not called
        flow.subcommand.check.assert_not_called()

    @mock.patch('compose_flow.commands.subcommands.env.Env.rw_env', new=True)
    @mock.patch('compose_flow.commands.workflow.settings')
    @mock.patch('compose_flow.commands.subcommands.env.utils')
    @mock.patch('compose_flow.commands.subcommands.env.get_backend')
    def test_update_version(self, *mocks):
        """
        Ensures that version in env is updated when the publish command is run
        """
        settings_mock = mocks[2]
        settings_mock.DOCKER_IMAGE_PREFIX = 'test.registry'
        settings_mock.LOGGING = {
            'version': 1,
            'loggers': {
                'compose_flow': {
                },
            },
        }

        version = '1.2.3'
        new_version = '0.9.999'
        docker_image = 'foo:bar'

        utils_mock = mocks[1]
        utils_mock.get_tag_version.return_value = new_version
        utils_mock.render = utils.render

        command = shlex.split('-e dev publish')
        flow = Workflow(argv=command)

        publish = flow.subcommand
        publish.get_built_docker_images = mock.Mock()
        publish.get_built_docker_images.return_value = []

        flow.run()

        env = flow.environment

        self.assertEqual(utils_mock.get_tag_version.return_value, env.data['VERSION'])
        self.assertEqual(f'test.registry/testdirname:{new_version}', env.data['DOCKER_IMAGE'])

    @mock.patch('compose_flow.commands.subcommands.env.utils')
    @mock.patch('compose_flow.commands.subcommands.env.get_backend')
    def test_e2e_happy_path_publish_with_auto_tags(self, *mocks):
        new_version = '3.5.9'

        utils_mock = mocks[1]
        utils_mock.get_tag_version.return_value = new_version
        utils_mock.render = utils.render

        command = shlex.split('-e prod publish --tag-major-minor')
        flow = Workflow(argv=command)

        publish = flow.subcommand
        execute_mock = mock.MagicMock()
        publish.execute = execute_mock

        flow.run()

        target_executions = [
            ('docker push localhost.localdomain/testdirname:3.5.9', {'_fg': True}),
            ('docker tag localhost.localdomain/testdirname:3.5.9 localhost.localdomain/testdirname:3', {}),
            ('docker push localhost.localdomain/testdirname:3', {'_fg': True}),
            ('docker tag localhost.localdomain/testdirname:3.5.9 localhost.localdomain/testdirname:3.5', {}),
            ('docker push localhost.localdomain/testdirname:3.5', {'_fg': True})
        ]

        call_target_tuples = list(zip(execute_mock.call_args_list, target_executions))

        self.assertEqual(len(target_executions), len(call_target_tuples))
        for call, target_call in zip(execute_mock.call_args_list, target_executions):
            args, kwargs = call
            target_args, target_kwargs = target_call
            self.assertEqual((target_args,), args)
            self.assertEqual(target_kwargs, kwargs)

    @mock.patch('compose_flow.commands.subcommands.base.BaseSubcommand.execute')
    @mock.patch('compose_flow.commands.subcommands.env.utils')
    @mock.patch('compose_flow.commands.subcommands.env.get_backend')
    def test_ut_get_built_tagged_image_names(self, *mocks):
        """Ensure we return built docker image names."""
        new_version = '0.9.999'

        utils_mock = mocks[1]
        utils_mock.get_tag_version.return_value = new_version
        utils_mock.render = utils.render

        command = shlex.split('-e prod publish --auto-tag')
        flow = Workflow(argv=command)

        publish = flow.subcommand
        values = publish.get_built_tagged_image_names()
        self.assertEqual(['localhost.localdomain/testdirname:0.9.999'], values)
