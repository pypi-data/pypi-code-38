from unittest import TestCase, mock

from compose_flow import docker
from compose_flow.errors import DockerError, NoSuchConfig


class DockerTestCase(TestCase):
    def test_json_formatter_context(self, *mocks):
        """
        Ensures the JSON format context manager does the right thing
        """
        with docker.json_formatter('docker node ls') as json_command:
            self.assertEqual('docker node ls --format "{{ json . }}"', json_command)

    @mock.patch('compose_flow.docker.get_docker_json')
    def test_get_config_no_such_config(self, *mocks):
        """
        Ensure NoSuchConfig is raised
        """
        get_docker_json_mock = mocks[0]
        get_docker_json_mock.side_effect = DockerError('No such config')

        self.assertRaises(NoSuchConfig, docker.get_config, 'test')
