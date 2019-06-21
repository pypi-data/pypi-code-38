from unittest import TestCase, mock

from compose_flow.commands.subcommands.profile import Profile
from compose_flow.utils import yaml_load

from tests.utils import get_content


class ProfileTestCase(TestCase):
    def setUp(self):
        self.workflow = mock.Mock()

    def test_check_global_mode(self, *mocks):
        """
        Ensures the profile check does not fail when there is no constraint on a global service
        """
        profile = Profile(self.workflow)

        profile.load = mock.Mock()
        profile.load.return_value = get_content('profiles/global_no_constraints.yml')

        errors = profile._check_services(profile.check_constraints, profile.data)

        self.assertEqual(0, len(errors), errors)

    def test_check_no_constraints(self, *mocks):
        """
        Ensures the profile check fails when no constraints are found
        """
        profile = Profile(self.workflow)

        profile.load = mock.Mock()
        profile.load.return_value = get_content('profiles/no_constraints.yml')

        errors = profile._check_services(profile.check_constraints, profile.data)

        self.assertRegex(' '.join(errors), r'constraints not found')

    def test_check_no_node_constraints(self, *mocks):
        """
        Ensures the profile check fails when `node.` constraints are not found
        """
        profile = Profile(self.workflow)

        profile.load = mock.Mock()
        profile.load.return_value = get_content('profiles/no_node_constraints.yml')

        errors = profile._check_services(profile.check_constraints, profile.data)

        self.assertRegex(' '.join(errors), r'node constraints not found')

    def test_check_no_resources(self, *mocks):
        """
        Ensures the profile check fails when no resource constraints are found
        """
        profile = Profile(self.workflow)

        profile.load = mock.Mock()
        profile.load.return_value = get_content('profiles/no_constraints.yml')

        errors = profile._check_services(profile.check_resources, profile.data)

        self.assertRegex(' '.join(errors), r'resource constraints not found')

    def test_check_resources_empty(self, *mocks):
        """
        Ensures the profile check fails when resources constraints are empty
        """
        profile = Profile(self.workflow)

        profile.load = mock.Mock()
        profile.load.return_value = get_content('profiles/resources_nothing_set.yml')

        errors = profile._check_services(profile.check_resources, profile.data)

        self.assertRegex(' '.join(errors), r'resource constraints not found')

    def test_check_with_node_constraints(self, *mocks):
        """
        Ensures the profile check passes when no constraints are found
        """
        profile = Profile(self.workflow)

        profile.load = mock.Mock()
        profile.load.return_value = get_content('profiles/with_node_constraints.yml')

        errors = profile._check_services(profile.check_constraints, profile.data)

        self.assertEqual(0, len(errors))

    def test_expand_services(self, *mocks):
        data = {
            'services': {
                'foo': {
                    'build': '..',
                    'image': '${DOCKER_IMAGE}',
                    'environment': [
                        'FOO=1',
                        'SPARK_WORKER_PORT=8888',
                        'SPARK_WORKER_WEBUI_PORT=8080',
                    ],
                    'ports': ['8000:8000'],
                    'deploy': {'replicas': 3},
                }
            },
            'compose_flow': {
                'expand': {
                    'foo': {
                        'increment': {
                            'env': ['SPARK_WORKER_PORT', 'SPARK_WORKER_WEBUI_PORT'],
                            'ports': {'source_port': True, 'destination_port': True},
                        }
                    }
                }
            },
        }

        profile = Profile(self.workflow)
        new_data = profile._check_cf_config(data)

        self.assertEqual(len(new_data['services']), 3)

        self.assertEqual(sorted(new_data['services'].keys()), ['foo1', 'foo2', 'foo3'])

        self.assertEqual(
            [x['ports'] for x in new_data['services'].values()],
            [['8000:8000'], ['8001:8001'], ['8002:8002']],
        )

        self.assertEqual(
            [x['environment'] for x in new_data['services'].values()],
            [
                ['FOO=1', 'SPARK_WORKER_PORT=8888', 'SPARK_WORKER_WEBUI_PORT=8080'],
                ['FOO=1', 'SPARK_WORKER_PORT=8889', 'SPARK_WORKER_WEBUI_PORT=8081'],
                ['FOO=1', 'SPARK_WORKER_PORT=8890', 'SPARK_WORKER_WEBUI_PORT=8082'],
            ],
        )

    def test_profile_no_compose_dir(self, *mocks):
        """
        when there is no compose directory, do not attempt to render a profile
        """
        profile = Profile(self.workflow)

    @mock.patch('compose_flow.commands.subcommands.profile.open')
    def test_profile_writes_once(self, *mocks):
        open_mock = mocks[0]

        profile = Profile(self.workflow)

        profile.load = mock.Mock()
        profile.load.return_value = 'services:'

        profile.write()
        profile.write()
        profile.write()

        self.assertEqual(1, open_mock.call_count)

    @mock.patch('compose_flow.commands.subcommands.profile.merge_profile')
    def test_set_resources_empty_resources_left_alone(self, *mocks):
        """
        Ensures when services.x.deploy doesn't exist it is not added
        """
        content = get_content('profiles/no_constraints.yml')
        data = yaml_load(content)

        service_name, data = list(data['services'].items())[0]

        profile = Profile(self.workflow)

        profile.set_resources(service_name, data)

        self.assertEqual('deploy' not in data, True)

    @mock.patch('compose_flow.commands.subcommands.profile.merge_profile')
    def test_set_resources_memory_limit_no_reservation(self, *mocks):
        """
        Ensures memory reservation is matched to limit when no reservation is given
        """
        merge_profile_mock = mocks[0]
        merge_profile_mock.return_value = get_content('profiles/limit_no_reservation.yml')

        profile = Profile(self.workflow)

        param = {}
        content = profile._compile(param)  # the param is ignored because it's using the mock

        merge_profile_mock.assert_called_with(param)

        data = yaml_load(content)
        resources = data['services']['app']['deploy']['resources']

        self.assertEqual(resources['reservations']['memory'], resources['limits']['memory'])

    @mock.patch('compose_flow.commands.subcommands.profile.merge_profile')
    def test_set_resources_memory_limit_and_reservation(self, *mocks):
        """
        Ensures memory reservation and limit are left alone when they are both defined
        """
        merge_profile_mock = mocks[0]
        merge_profile_mock.return_value = get_content('profiles/limit_and_reservation.yml')

        profile = Profile(self.workflow)

        param = {}
        content = profile._compile(param)  # the param is ignored because it's using the mock

        merge_profile_mock.assert_called_with(param)

        data = yaml_load(content)
        resources = data['services']['app']['deploy']['resources']

        self.assertEqual('10M', resources['reservations']['memory'])
        self.assertEqual('100M', resources['limits']['memory'])

    @mock.patch('compose_flow.commands.subcommands.profile.merge_profile')
    def test_set_resources_memory_reservation_no_limit(self, *mocks):
        """
        Ensures memory limit is matched to reservation when no limit is given
        """
        merge_profile_mock = mocks[0]
        merge_profile_mock.return_value = get_content('profiles/reservation_no_limit.yml')

        profile = Profile(self.workflow)

        param = {}
        content = profile._compile(param)  # the param is ignored because it's using the mock

        merge_profile_mock.assert_called_with(param)

        data = yaml_load(content)
        resources = data['services']['app']['deploy']['resources']

        self.assertEqual(resources['limits']['memory'], resources['reservations']['memory'])
