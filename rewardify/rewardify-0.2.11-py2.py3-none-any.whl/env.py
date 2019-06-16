# Standard library
import platform
import os
import importlib.util
import ast
import logging

from typing import NoReturn, Dict

# Third party
from peewee import SqliteDatabase, MySQLDatabase, PostgresqlDatabase

from jinja2 import FileSystemLoader, Environment

# Local imports
from rewardify.models import User, Reward, Pack, DATABASE_PROXY

from rewardify._util import Singleton, PATH


FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))


# #################################
# DATABASE CONFIGURATION MANAGEMENT
# #################################


class DatabaseConfig:
    """
    Instances of this class manage the configuration of tha database for the project. This includes the engine, host,
    port, username, password and database name.

    The typical work flow using this class is the following:
    A new object is created from a config dict. Then the database is init-ed (meaning the object is created)
    Then the database proxy (placeholder) for the models is connected to this database object at run time and then the
    database is actually connected to its persistent counterpiece (file for sqlite, server for mysql):

    EXAMPLE:
    database_config = DatabaseConfig.from_dict(database_dict)
    database_config.init()
    database_proxy.initialize(database_config.get())
    database_config.connect()
    database_config.create_tables() # OPTIONAL

    CHANGELOG

    Added 09.06.2019
    """
    # This dict will be used as the default base dict, when a new DatabaseConfig object is to be created from a dict,
    # which may not contain all the keys. For the keys that are not present, the default ones will stay, but will
    # otherwise be overwritten.
    DEFAULT_DICT = {
        'engine':       'sqlite',
        'host':         ':memory:',
        'database':     '',
        'user':         '',
        'password':     '',
        'port':         0
    }

    # A list of all valid engine strings
    SUPPORTED_ENGINES = [
        'sqlite',
        'mysql',
        'postgres'
    ]

    # This is a list, that contains all the model classes of this project. This list is needed to be passed
    # to the database to create all the tables
    MODELS = [
        User,
        Reward,
        Pack
    ]

    # INSTANCE CONSTRUCTION
    # ---------------------

    def __init__(self,
                 engine: str,
                 host: str,
                 database: str,
                 user: str,
                 password: str,
                 port: int) -> NoReturn:
        # This will raise an error, if the engine string is not a valid one
        self.check_engine(engine)

        self.engine = engine
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

        # Later on this variable will contain the actual database instance
        self.instance = None

    def check_engine(self, engine: str):
        """
        This will raise a value error if the engine string is not one of the supported engines.

        CHANGELOG

        Added 09.06.2019

        :param engine:
        :return:
        """
        if engine not in self.SUPPORTED_ENGINES:
            raise ValueError('The engine "{}" is not supported'.format(engine))

    # CREATING DATABASE INSTANCE
    # --------------------------

    def init(self):
        """
        This method will create a new database object and put it into the "self.instance" variable. The type of
        database object created depends on the value of the engine string

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        # Basically I am using this dict as a "switch" statement to reduce "if"-clutter
        engine_create_methods = {
            'sqlite':       self.init_sqlite,
            'mysql':        self.init_mysql,
            'postgres':     self.init_postgres
        }
        engine_create_methods[self.engine]()

    def init_sqlite(self):
        """
        Creates a new sqlite database object and puts it into "self.instance"
        NOTE: For the creation of a sqlite database only the path to the file is relevant. The "self.host" variable
        will be used as the sqlite string

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        self.instance = SqliteDatabase(self.host)

    def init_mysql(self):
        """
        Creates a new mysql database object and puts it into the "self.instance".

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        self.instance = MySQLDatabase(
            self.database,
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port
        )

    def init_postgres(self):
        """
        Creates a new postgrsql database object and puts it into the "self.instance"

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        self.instance = PostgresqlDatabase(
            self.database,
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port
        )

    # DATABASE OPERATIONS
    # -------------------

    def connect(self):
        """
        When a database object has already been created, this method actually connects the object in "self.instance"
        to the actual persistent database.

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        self.instance.connect()

    def create_tables(self):
        """
        If the database object is already connected and created, this method will create the tables for all the models
        of the rewardify project into this database.

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        self.instance.create_tables(self.MODELS)

    def drop_tables(self):
        """
        If the database object is already connected and created, this method will drop the tables for all the models
        of the rewardify project into this database.

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        self.instance.drop_tables(self.MODELS)

    def get(self):
        """
        returns the database object

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        return self.instance

    # UTILITY METHODS
    # ---------------

    def update(self, database_dict: Dict) -> NoReturn:
        """
        Given a database dict, all the internal values will be updated according to this dict

        CHANGELOG

        Added 09.06.2019

        :param database_dict:
        :return:
        """
        for key, value in database_dict.items():
            setattr(self, key, value)

    # CLASS METHODS
    # -------------

    @classmethod
    def from_dict(cls, database_dict):
        """
        Given a dict, which contains the database config, this method will create and return a new DatabaseConfig
        object from it.
        The dict can contain any subset of the following keys, every key not used it substituted with the default item:
        - engine
        - host
        - database
        - port
        - user
        - password

        CHANGELOG

        Added 09.06.2019

        :param database_dict:
        :return:
        """
        # We will use the default dict as a base line (in case not all keys are provided by the given dict as for the
        # case of sqlite. Then we replace all possible values with the actual ones
        argument_dict = cls.DEFAULT_DICT
        argument_dict.update(database_dict)

        # Finally we can pass the arguments to the constructor by unpacking the dict
        return cls(**argument_dict)


# ######################
# CONFIG FILE MANAGEMENT
# ######################


@Singleton
class EnvironmentConfig:

    # CLASS VARIABLES
    # ---------------

    PLATFORM_FOLDER_PATHS = {
        'Linux': '/opt/.rewardify',
        'Darwin': 'NONE',
        'Windows': 'NONE'
    }

    CONFIG_FILE_NAME = 'config.py'

    TEMPLATE_FOLDER_PATH = os.path.join(FOLDER_PATH, 'templates')
    TEMPLATE_LOADER = FileSystemLoader(searchpath=TEMPLATE_FOLDER_PATH)
    TEMPLATE_ENVIRONMENT = Environment(loader=TEMPLATE_LOADER)

    # THE DEFAULT VALUES
    # ------------------

    DEFAULT_DATABASE_DICT = {}

    DEFAULT_BACKEND_CLASS = None

    def __init__(self):
        # First of all, we need to know in which folder the config is even located in. This is dependant on the
        # platform, but inconfigureable for each platform.
        # We use the mapping of the platform to the folder path
        self.platform = platform.system()
        self.folder_path = self.PLATFORM_FOLDER_PATHS[self.platform]

        # Creating a new database configuration object from the default
        self.database_config = DatabaseConfig.from_dict(self.DEFAULT_DATABASE_DICT)

        self.backend_class = self.DEFAULT_BACKEND_CLASS

    def set_folder_path(self, folder_path):
        self.folder_path = folder_path

    def load(self):
        self.load_config()
        self.load_database()

    def load_config(self):
        config_file_path = os.path.join(self.folder_path, self.CONFIG_FILE_NAME)

        # Here we are dynamically importing the config python module using its file path
        spec = importlib.util.spec_from_file_location('config', config_file_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        source = self.read_file(config_file_path)

        # Now we parse the module to obtain all the variable names
        root = ast.parse(source, filename=config_file_path)
        names = sorted({node.id for node in ast.walk(root) if isinstance(node, ast.Name)})

        for name in names:
            setattr(self, name, getattr(config, name))

    def load_database(self):
        self.database_config = DatabaseConfig.from_dict(self.DATABASE)

    def init(self):
        """
        CHANGELOG

        Added 16.06.2019
        :return:
        """
        self.database_config.init()
        DATABASE_PROXY.initialize(self.database_config.instance)
        self.database_config.connect()

    def read_file(self, file_path: str):
        with open(file_path, mode='r+') as file:
            content = file.read()
        return content

    # CHECKING METHODS
    # ----------------

    def config_folder_exists(self) -> bool:
        """
        Returns True if the config folder path exists, False otherwise

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        return os.path.exists(self.folder_path) and os.path.isdir(self.folder_path)


# ###############################
# INSTALLATION OF THE ENVIRONMENT
# ###############################


class EnvironmentInstaller:
    """
    This is a class, that is supposed to help with the creation of the config environment during the installation
    process.
    This includes the creation of the folder, which will contain all the files relevant to rewardify, the creation of
    a sample config.py file and the creation of a rewardify.db sqlite file, which is already set up to contain the
    needed tables

    CHANGELOG

    Added 14.06.2019
    """

    PLATFORM_CONFIG_FOLDER_NAME = {
        'Linux':            '.rewardify',
        'Darwin':           'rewardify',
        'Windows':          'Rewardify'
    }

    DATABASE_FILE_NAME = "rewardify.db"

    CONFIG_FILE_NAME = "config.py"
    CONFIG_FILE_TEMPLATE = "config.jinja2"

    # CONFIGURATION FOR JINJA TEMPLATING
    # ----------------------------------

    TEMPLATE_FOLDER_PATH = os.path.join(PATH, 'templates')
    TEMPLATE_LOADER = FileSystemLoader(searchpath=TEMPLATE_FOLDER_PATH)
    TEMPLATE_ENVIRONMENT = Environment(loader=TEMPLATE_LOADER)

    # INSTANCE CONSTRUCTION
    # ---------------------

    def __init__(self, install_path: str):
        """
        The constructor.

        CHANGELOG

        Added 14.06.2019

        :param install_path:
        """
        self.logger = logging.getLogger('Installation')
        self.platform = platform.system()

        self.path = install_path

    # INSTALLATION PROCESS
    # --------------------

    def install(self):
        """
        This method will perform the install of the envrionment: Create the folder, the "config.py" and the
        "rewardify.db"

        CHANGELOG

        Added 14.06.2019

        :return:
        """
        self.create_config_folder()
        self.create_config_file()
        self.create_database_file()

    def create_database_file(self):
        """
        Creates the database file "rewardify.db" and creates the necessary tables into the sqlite database

        CHANGELOG

        Added 14.06.2019

        :return:
        """
        database_file_path = self.get_database_file_path()
        self.create_empty_file(database_file_path)

        database = SqliteDatabase(database_file_path)
        DATABASE_PROXY.initialize(database)
        database.connect()
        database.create_tables([User, Pack, Reward])
        database.close()

    def create_config_file(self):
        config_file_path = self.get_config_file_path()
        self.create_file_from_template(
            config_file_path,
            self.CONFIG_FILE_TEMPLATE,
            {}
        )

    def create_config_folder(self):
        config_folder_path = self.get_config_folder_path()
        os.makedirs(config_folder_path)
        self.logger.info('Created config folder at PATH "{}"'.format(config_folder_path))

    # HELPER METHODS
    # --------------

    def get_config_folder_path(self):
        config_folder_name = self.PLATFORM_CONFIG_FOLDER_NAME[self.platform]
        return os.path.join(self.path, config_folder_name)

    def get_database_file_path(self):
        config_folder_path = self.get_config_folder_path()
        return os.path.join(config_folder_path, self.DATABASE_FILE_NAME)

    def get_config_file_path(self):
        config_folder_path = self.get_config_folder_path()
        return os.path.join(config_folder_path, self.CONFIG_FILE_NAME)

    @classmethod
    def create_file_from_template(cls, file_path: str, template_name: str, context: Dict):
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

    @classmethod
    def create_empty_file(cls, file_path: str):
        """
        Given a file path, this method will create that file empty. If the file already exists, it will override the
        content with an empty string

        CHANGELOG

        Added 14.06.2019

        :param file_path:
        :return:
        """
        with open(file_path, mode="w+") as file:
            file.write("")
