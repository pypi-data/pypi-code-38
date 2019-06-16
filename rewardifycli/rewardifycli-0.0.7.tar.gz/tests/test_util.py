# standard library
import os

# third party
from rewardify.models import User

from rewardify.main import Rewardify

# local
from rewardifycli.__internal.tests import RewardifycliTestCase
from rewardifycli.__internal.tests import MockConfigContext, StandardUserContext

from rewardifycli.util import UserCredentials
from rewardifycli.util import login_required


class TestContextManagers(RewardifycliTestCase):

    def test_mock_config_context_manager(self):
        with MockConfigContext(self, mock_users=["Jonas", "Joana"]) as mock_context:
            self.assertTrue(os.path.exists(self.FOLDER_PATH))
            config_file_path = os.path.join(self.FOLDER_PATH, 'config.py')
            self.assertTrue(os.path.exists(config_file_path))

            self.assertTrue(len(mock_context.users), 2)

    def test_standard_user_context_manager(self):
        with StandardUserContext() as user_context:
            query = User.select().where(User.name == user_context.username)
            self.assertEqual(len(query), 1)
            user = query[0]
            self.assertIsInstance(user_context.user, User)
            self.assertEqual(user.name, user_context.user.name)

    def test_user_and_config_manager_together(self):
        with StandardUserContext() as user_context, MockConfigContext(self) as mock_context:
            facade: Rewardify = Rewardify.instance()

            self.assertTrue(facade.exists_user(user_context.username))


class TestUserCredentials(RewardifycliTestCase):

    def test_creation_of_file_working(self):
        with MockConfigContext(self) as mock_context:
            credentials: UserCredentials = UserCredentials.instance()
            credentials.load()
            self.assertEqual(mock_context.credentials, credentials)
            self.assertTrue(credentials.is_default())

            self.assertTrue(os.path.exists(credentials.get_path()))

    def test_saving_new_credentials(self):
        with MockConfigContext(self) as mock_context:
            credentials: UserCredentials = UserCredentials.instance()
            credentials.save('Jonas', 'secret')
            credentials.load()

            self.assertTrue(credentials.exists())
            self.assertEqual(credentials['username'], 'Jonas')
            self.assertEqual(credentials['password'], 'secret')

            self.assertFalse(credentials.is_default())
