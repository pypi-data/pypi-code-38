# Standard library
import platform
import os
import shutil

from unittest import TestCase

from typing import Dict, List

# Third party
from peewee import SqliteDatabase

from jinja2 import Environment, FileSystemLoader

# Local imports
from rewardify.models import DATABASE_PROXY
from rewardify.models import User, Pack, Reward

from rewardify.env import EnvironmentConfig


PATH = os.path.dirname(os.path.abspath(__file__))


# ###########
# FOR TESTING
# ###########


# THE MIXINS
# ----------


class ConfigTestMixin:
    """
    This class implements TestCase behaviour to create a new config folder and configure the
    ConfigEnvironment to use this correctly on class setup.
    It also implements various additional helper methods, that can be used to create custom config
    environments for each test method.

    CHANGELOG

    Added 10.06.2019
    """
    # OVERWRITING THE CONFIG PATH OF THE ENV
    # --------------------------------------

    # According to the operation system, on which the program is being run, a different path has to be used for the
    # config folder. This mapping assigns the path to be used for testing to each operating system returned by
    # "platform.system"
    PLATFORM_TEST_CONFIG_PATHS = {
        'Linux': '/tmp/rewardify',
        'Darwin': '',
        'Windows': '',
    }

    # This field will store the path which was originally set within the ConfigEnvironment, it will be used to reset
    # "everything back to how we found it" at tear down
    ORIGINAL_FOLDER_PATH = ''
    # This field will store the actual folder path to the config folder after the decision based on the operating
    # system has been made.
    FOLDER_PATH = ''

    # FOR TEMPLATING THE CONFIG FILES
    # -------------------------------

    TEMPLATE_FOLDER_PATH = os.path.join(PATH, 'templates', 'test')
    TEMPLATE_LOADER = FileSystemLoader(searchpath=TEMPLATE_FOLDER_PATH)
    TEMPLATE_ENVIRONMENT = Environment(loader=TEMPLATE_LOADER)

    CONFIG_TEMPLATE_NAME = 'config.jinja2'
    CONFIG_FILE_NAME = 'config.py'

    # ################
    # INSTANCE METHODS
    # ################

    def setUp(self):
        """
        This method is called before the execution of every test method. It calls the "clean" method, which deletes all
        the files from the config folder, so the test method starts out with a clean slate.

        CHANGELOG

        Added 10.06.2019

        :return:
        """
        self.clean()

    # #############
    # CLASS METHODS
    # #############

    @classmethod
    def setUpClass(cls):
        """
        This method is called before any of the test methods of this class are being executed. It creates the config
        folder to be used for testing and configures the ConfigEnvironment singleton to use this path instead of its
        default install location.

        CHANGELOG

        Added 10.06.2019

        :return:
        """
        # We find out, which path to use for the testing by querying the current operating system
        platform_string = platform.system()
        cls.FOLDER_PATH = cls.PLATFORM_TEST_CONFIG_PATHS[platform_string]

        # Now we save the original path of the ConfigEnvironment and replace it with the testing path
        environment_config = EnvironmentConfig.instance()  # type: EnvironmentConfig
        cls.ORIGINAL_FOLDER_PATH = environment_config.folder_path
        environment_config.set_folder_path(cls.FOLDER_PATH)

        # Now we only need to create the config folder
        cls.create_config_folder()

    @classmethod
    def create_config_folder(cls):
        """
        This method creates a new folder with the path "cls.FOLDER_PATH", if it does not already exist

        CHANGELOG

        Added 10.06.2019

        :return:
        """
        if not os.path.exists(cls.FOLDER_PATH):
            os.makedirs(cls.FOLDER_PATH)

    @classmethod
    def tearDownClass(cls):
        # Now we set back the original folder path
        environment_config: EnvironmentConfig = EnvironmentConfig.instance()
        environment_config.set_folder_path(cls.ORIGINAL_FOLDER_PATH)

    @classmethod
    def create_config(cls,
                      imports: List,
                      database_dict: Dict,
                      backend,
                      rewards: List,
                      packs: List,
                      plugin_code: str):
        """
        Given a list with python code strings for import statements "imports", a dict defining the database access
        "database_dict", the string containing the class name of the backend class to be used "backend", a list
        defining the available "rewards" and "packs" and a python code string for additional variable definitions in
        the config file, that might be needed by plugins.
        This method uses all of these to create a new "config.py" file in the "cls.FOLDER_PATH" based on
        the template for the config file

        CHANGELOG

        Added 10.06.2019

        :param imports:
        :param database_dict:
        :param backend:
        :param rewards:
        :param packs:
        :param plugin_code:
        :return:
        """
        context = {
            'imports':      imports,
            'db':           database_dict,
            'backend':      backend,
            'rewards':      rewards,
            'packs':        packs,
            'plugin':       plugin_code
        }
        config_file_path = os.path.join(cls.FOLDER_PATH, cls.CONFIG_FILE_NAME)
        cls.file_from_template(
            config_file_path,
            cls.CONFIG_TEMPLATE_NAME,
            context
        )

        # When a new config file is created, we obviously want to see these changes in the config object as well,
        # this is why we are reloading the config object with the new config file
        environment_config: EnvironmentConfig = EnvironmentConfig.instance()
        environment_config.load()

    # HELPER METHODS
    # --------------

    @classmethod
    def clean(cls):
        """
        This method deletes all the files within the "cls.FOLDER_PATH"

        CHANGELOG

        Added 10.06.2019

        :return:
        """
        for the_file in os.listdir(cls.FOLDER_PATH):
            file_path = os.path.join(cls.FOLDER_PATH, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    @classmethod
    def get_config_file_path(cls):
        """
        This method returns the file path to the "config.py" file within the testing config folder

        CHANGELOG

        Added 10.06.2019

        :return:
        """
        return os.path.join(cls.FOLDER_PATH, cls.CONFIG_FILE_NAME)

    @classmethod
    def file_from_template(cls, file_path: str, template_name: str, context: Dict):
        """
        Given the string path of a file to be written to, the name of the template (within the defined template folder)
        and a dict defining the context of for the jinja template, this method will render the template with the
        context and save the result into the given file path.

        CHANGELOG

        Added 10.06.2019

        :param file_path:
        :param template_name:
        :param context:
        :return:
        """
        # First we render the template content into a plain string and then we save the string into the
        # file (overwriting all the content)
        template = cls.TEMPLATE_ENVIRONMENT.get_template(template_name)
        content = template.render(**context)

        with open(file_path, mode='w+') as file:
            file.write(content)


class DBTestMixin:
    """
        This is a abstract base class, which adds additional setUp and tearDown steps to create a fresh
        in memory database before each test method is being executed, which enables the work with the model classes.

        CHANGELOG

        Added 09.06.2019
        """
    TEST_DATABASE = SqliteDatabase(':memory:')
    MODELS = [
        User,
        Pack,
        Reward
    ]

    def setUp(self):
        """
        This method is being called before each test method is executed.
        It creates a new in-memory database according to the models configured in the "models.py" file of
        this project

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        # Here we bind the database proxy (placeholder) for which we have defined the models
        # to the test database
        DATABASE_PROXY.initialize(self.TEST_DATABASE)
        self.TEST_DATABASE.connect()
        self.TEST_DATABASE.create_tables(self.MODELS)

    def tearDown(self):
        """
        This method is being called after each test method was executed.
        It closes the database that was created for the test method

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        self.TEST_DATABASE.drop_tables(self.MODELS)
        self.TEST_DATABASE.close()


# ACTUAL ABSTRACT TEST CASE BASE CLASSES
# --------------------------------------


class ConfigTestCase(ConfigTestMixin, TestCase):

    pass


class DBTestCase(DBTestMixin, TestCase):

    pass


class RewardifyTestCase(ConfigTestMixin, DBTestMixin, TestCase):

    def setUp(self):
        ConfigTestMixin.setUp(self)
        DBTestMixin.setUp(self)

