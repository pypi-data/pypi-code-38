from functools import lru_cache
from unittest import TestCase, mock

from compose_flow.commands.subcommands.remote import Remote

TEST_USERNAME = 'testuser'


@mock.patch('compose_flow.settings.DEFAULT_CF_REMOTE_USER', new=TEST_USERNAME)
class RemoteTestCase(TestCase):
    @property
    @lru_cache()
    def workflow(self):
        return mock.Mock()

    def test_default_username(self):
        """
        Ensure when no app config is found, the username from settings module is used
        """
        self.workflow.app_config = {}

        remote = Remote(self.workflow)

        self.assertEqual(remote.username, TEST_USERNAME)

    def test_appconfig_remote_without_username(self):
        """
        Ensure username falls back to the settings user when there is no '@' in the remote hostname
        """
        self.workflow.args.environment = 'dev'
        self.workflow.app_config = {
            'remotes': {
                'dev': {
                    'ssh': f'testremotehost'
                },
            },
        }

        remote = Remote(self.workflow)

        self.assertEqual(remote.username, TEST_USERNAME)

    def test_username_from_appconfig(self):
        """
        Ensure username is extracted from remote host
        """
        username = 'testuser'

        self.workflow.args.environment = 'dev'
        self.workflow.app_config = {
            'remotes': {
                'dev': {
                    'ssh': f'{username}@testremotehost'
                },
            },
        }

        remote = Remote(self.workflow)

        self.assertEqual(remote.username, username)
