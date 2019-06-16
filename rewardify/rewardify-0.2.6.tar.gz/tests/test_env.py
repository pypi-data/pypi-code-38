# Standard library
import os
import shutil
import platform

from unittest import TestCase

# Third party
from peewee import SqliteDatabase

from jinja2 import FileSystemLoader, Environment

# Local imports
from rewardify.env import DatabaseConfig
from rewardify.env import EnvironmentConfig
from rewardify.env import EnvironmentInstaller

from rewardify.models import User
from rewardify.models import DATABASE_PROXY

from rewardify._util_test import ConfigTestCase


FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))


class TestDatabaseConfig(TestCase):

    # CLASS VARIABLES
    # ---------------

    SAMPLE_DATABASE_DICT = {
        'engine':       'sqlite',
        'host':         ':memory:'
    }

    # ACTUAL TEST CASES
    # -----------------

    def test_object_creation(self):
        database_config = DatabaseConfig(
            'sqlite',
            ':memory:',
            '',
            '',
            '',
            0
        )
        self.assertEqual(database_config.engine, 'sqlite')

    def test_object_creation_from_dict(self):
        database_dict = {
            'engine':       'postgres',
            'user':         'Jonas',
            'host':         'localhost'
        }
        database_config = DatabaseConfig.from_dict(database_dict)

        self.assertIsInstance(database_config, DatabaseConfig)
        self.assertEqual(database_config.user, 'Jonas')

    def test_checking_engine_string_validity(self):
        database_config = DatabaseConfig.from_dict({'engine': 'sqlite'})
        self.assertEqual(database_config.engine, 'sqlite')

        self.assertRaises(
            ValueError,
            DatabaseConfig.from_dict,
            {'engine':  'yolo-db'}
        )

    def test_database_object_creation_sqlite(self):
        database_config = self.get_sample_object()
        database_config.init()

        self.assertIsInstance(database_config.get(), SqliteDatabase)

    def test_sqlite_database(self):
        database_config = self.get_sample_object()
        database_config.init()
        DATABASE_PROXY.initialize(database_config.get())
        database_config.connect()
        database_config.create_tables()

        # Creating a user and saving it just to see if it works
        user = User(
            name="Jonas",
            password="secret",
            dust=0,
            gold=0,
        )
        user.save()

    # HELPER METHODS
    # --------------

    def get_sample_object(self):
        return DatabaseConfig.from_dict(self.SAMPLE_DATABASE_DICT)


class TestEnvironmentConfig(ConfigTestCase):

    SAMPLE_IMPORTS = [
        'from rewardify.backends import AbstractBackend'
    ]

    SAMPLE_DATABASE_DICT = {
        'engine':       'sqlite',
        'host':         ':memory:',
        'database':     '',
        'user':         '',
        'password':     '',
        'port':         0
    }

    SAMPLE_PACKS = [

    ]

    SAMPLE_REWARDS = [

    ]

    SAMPLE_BACKEND = 'MockBackend'

    SAMPLE_PLUGIN_CODE = 'MOCK_BACKEND_USERS = ["Jonas"]'

    # ACTUAL TEST METHODS
    # -------------------

    def test_config_test_case_working(self):
        self.assertTrue(os.path.exists(self.FOLDER_PATH))

    def test_create_config(self):
        self.setup_sample()
        self.assertTrue(os.path.exists(self.get_config_file_path()))

    def test_load_config_file(self):
        self.setup_sample()

        environment_config: EnvironmentConfig = EnvironmentConfig.instance()
        environment_config.load_config()

        self.assertTrue(hasattr(environment_config, 'DATABASE'))
        self.assertTrue(hasattr(environment_config, 'BACKEND'))

    # HELPER METHODS
    # --------------

    def setup_sample(self):
        # Setting up the config-py file
        self.create_config(
            self.SAMPLE_IMPORTS,
            self.SAMPLE_DATABASE_DICT,
            self.SAMPLE_BACKEND,
            self.SAMPLE_REWARDS,
            self.SAMPLE_PACKS,
            self.SAMPLE_PLUGIN_CODE
        )


class TestEnvironmentInstaller(TestCase):

    FOLDER_PATH = '/tmp/rewardify'

    # SETTING UP
    # ----------

    def setUp(self):
        # Before every test, we need to clean up the environment
        installation_folder_path = self.get_installation_path()
        if os.path.exists(installation_folder_path):
            shutil.rmtree(installation_folder_path)

    # ACTUAL TESTS
    # ------------

    def test_init_working(self):
        installer = EnvironmentInstaller(self.FOLDER_PATH)
        self.assertEqual(installer.path, self.FOLDER_PATH)

    def test_get_file_paths(self):
        installer = EnvironmentInstaller(self.FOLDER_PATH)
        folder_path = os.path.join(self.FOLDER_PATH, installer.PLATFORM_CONFIG_FOLDER_NAME[platform.system()])
        self.assertEqual(
            installer.get_config_folder_path(),
            folder_path
        )
        self.assertEqual(
            installer.get_config_file_path(),
            os.path.join(folder_path, installer.CONFIG_FILE_NAME)
        )
        self.assertEqual(
            installer.get_database_file_path(),
            os.path.join(folder_path, installer.DATABASE_FILE_NAME)
        )

    def test_config_file_created(self):
        installer = EnvironmentInstaller(self.FOLDER_PATH)
        installer.create_config_folder()
        installer.create_config_file()

        self.assertTrue(os.path.exists(installer.get_config_file_path()))

    def test_database_file_created(self):
        installer = EnvironmentInstaller(self.FOLDER_PATH)
        installer.create_config_folder()
        installer.create_database_file()

        self.assertTrue(os.path.exists(installer.get_database_file_path()))

    def test_database_creation_successful(self):
        installer = EnvironmentInstaller(self.FOLDER_PATH)
        installer.create_config_folder()
        installer.create_database_file()

        self.assertTrue(os.path.exists(installer.get_database_file_path()))
        # The Database should be connected to the models now, which one should be able to create a new model and
        # insert it into the database
        user = User(
            name="Jonas",
            password="Secret",
            gold=0,
            dust=0
        )
        user.save()
        self.assertIsInstance(user, User)

    def test_config_creation_successful(self):
        installer = EnvironmentInstaller(self.FOLDER_PATH)
        installer.create_config_folder()
        installer.create_config_file()

        self.assertTrue(os.path.exists(installer.get_config_file_path()))
        with open(installer.get_config_file_path(), mode="r") as file:
            content = file.read()
            self.assertTrue("DATABASE" in content)
            self.assertTrue("BACKEND" in content)
            self.assertTrue("MOCK_BACKEND_USERS" in content)

    # HELPER METHODS
    # --------------

    def get_installation_path(self):
        return os.path.join(self.FOLDER_PATH, EnvironmentInstaller.PLATFORM_CONFIG_FOLDER_NAME[platform.system()])
