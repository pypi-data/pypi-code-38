# standard library
import os
import shutil

from typing import Dict

# third party
import click

from jinja2 import FileSystemLoader, Environment

from rewardify.env import EnvironmentConfig

from rewardify.main import Rewardify

# local
from rewardifycli.__internal.util import Singleton

# ######################
# PROJECT WIDE CONSTANTS
# ######################

PATH = os.path.dirname(os.path.abspath(__file__))

# ##########
# TEMPLATING
# ##########


@Singleton
class Templater:
    """
    This singleton wraps the templating functionality for the project. The "use_template" method returns the string
    result after using the given context on the template with the given name.

    CHANGELOG

    Added 14.06.2019
    """
    def __init__(self):
        """
        The constructor.

        CHANGELOG

        Added 14.06.2019
        """
        self.folder_path = os.path.join(PATH, 'templates')
        self.loader = FileSystemLoader(searchpath=self.folder_path)
        self.environment = Environment(loader=self.loader)

    def use_template(self, name: str, context: Dict) ->str:
        """
        Given the name of the template and the context dict (all the values that have to be accessible from within the
        template), this method will return the resulting string after using the context on the template.

        CHANGELOG

        Added 14.06.2019

        :param name:
        :param context:
        :return:
        """
        template = self.environment.get_template(name)
        content = template.render(**context)
        return content

    def echo_template(self, name: str, context: Dict):
        """
        Given the name of a template in the templates folder and the context dict, this method will echo the result of
        the template rendering through "click.echo" directly to the console

        CHANGELOG

        Added 15.06.2019

        :param name:
        :param context:
        :return:
        """
        content = self.use_template(name, context)
        click.echo(content)


# #################
# LOGIN PERSISTENCY
# #################

def login_required(func):
    """
    This is a decorator for the cli commands. It makes sure, that a valid user to perform the commands on is currently
    logged in. It does so by checking the credentials from the temp file with the facade object for the three cases:
    1) Is any user specified in the credentials file?
    2) Does a user with the given username even exist?
    3) Is the correct password for the user given

    !NOTE: It is important, that this is the first decorator applied to the function, which means, that it has to be
    closest to the function name, otherwise it will not work.

    CHANGELOG

    Added 15.06.2019

    Changed 16.06.2019
    Instead of returning a 1 in the case of the login being incorrect (which I previously thought to be the exit code
    for the command) a click.Abort() exception will be risen, which will actually cause the exit code 1 and a
    termination of the command.

    :param func:
    :param args:
    :param kwargs:
    :return:
    """
    def wrapper(*args, **kwargs):
        # UserCredentials is a singleton, that provides access to the credentials of the currently logged in user,
        # which are being saved in a temporary file
        credentials: UserCredentials = UserCredentials.instance()

        # The Rewardify object is the main facade to the rewardify system. It provides the methods for checking user
        # existence and the password.
        facade: Rewardify = Rewardify.instance()

        templater: Templater = Templater.instance()

        # Some of the templates user the username to display the error
        context = {'username': credentials['username']}

        if credentials.is_default():
            templater.echo_template('no_user.jinja2', context)
            raise click.Abort()

        if not facade.exists_user(credentials['username']):
            templater.echo_template('user_not_exists.jinja2', context)
            raise click.Abort()

        if not facade.user_check_password(credentials['username'], credentials['password']):
            templater.echo_template('wrong_password.jinja2', context)
            raise click.Abort()

        # Only if the user really truely is valid, the command is being executed
        return func(*args, **kwargs)

    # The doc string is a property of the function object, and usually the doc string of the original function would be
    # lost during decoration, but since we absolutely need the doc string for the command help text, we are expliccitly
    # copying here
    wrapper.__doc__ = func.__doc__

    return wrapper


@Singleton
class UserCredentials:
    """
    This is a singleton for easy access to the credentials of the currently logged in user.
    To access username and password just use the instance as a dict like object with the keys "username" and
    "password"

    CHANGELOG

    Added 14.06.2019
    """
    FILE_NAME = '.cli_login.txt'

    DEFAULT_CREDENTIALS = {
        'username':     '22e12933a058d3c0082a2899e20465582b9af176e2de4a4369206c3c450a6e8b',
        'password':     '09d1de35fbcc581d960ab74ab8f7e0c1f8bf6851c2800672253852d84e7eed5e'
    }

    def __init__(self):
        """

        """
        self.config: EnvironmentConfig = EnvironmentConfig.instance()
        self.credentials = {}
        self.load()

    def is_default(self) -> bool:
        """
        This method returns whether or not the current credentials are the default credentials.
        It is always then the default credentials, when currently no one is logged in!

        CHANGELOG

        Added 15.06.2019

        :return:
        """
        return self['username'] == self.DEFAULT_CREDENTIALS['username']

    def exists(self) -> bool:
        """
        Returns the boolean value of whether or not a credentials file exists

        CHANGELOG

        Added 14.06.2019

        :return:
        """
        path = self.get_path()
        return os.path.exists(path)

    def load(self):
        """
        CHANGELOG

        Added 14.06.2019

        :return:
        """
        # It is possible, that mainly during the first run of the program, the credentials file does not exist yet. In
        # this case a new one will be created with the default credentials.
        if not self.exists():
            self.save(**self.DEFAULT_CREDENTIALS)

        with open(self.get_path(), mode='r') as file:
            content = file.read()
            # The file contains the username and the password ins plain text, separated by a comma, with the username
            # being the first value and the password being the second
            content_split = content.split(',')
            self.credentials = {
                'username':     content_split[0],
                'password':     content_split[1]
            }

    def save(self, username: str, password: str):
        """
        Given the username and the password, this method will write a new credential file using these values

        CHANGELOG

        Added 14.06.2019

        Changed 16.06.2019
        After the changes are being saved to the file the load() method is being called, so that the changes are also
        made to the program instance.

        :param username:
        :param password:
        :return:
        """
        with open(self.get_path(), mode='w') as file:
            content = '{},{}'.format(username, password)
            file.write(content)

        # 16.06.2019
        # After the save method is called the new changes have to be loaded from the file into the credentials object,
        # so that the changes are actually visible to the program
        self.load()

    def delete(self):
        """
        Deletes the file for the credentials

        CHANGELOG

        Added 16.06.2019

        :return:
        """
        os.unlink(self.get_path())

    def get_path(self) -> str:
        """
        Returns the path to the file, which saves the credentials

        CHANGELOG

        Added 14.06.2019

        :return:
        """
        config_folder_path = self.config.folder_path
        credential_path = os.path.join(config_folder_path, self.FILE_NAME)
        return credential_path

    # MAGIC METHODS
    # -------------

    def __getitem__(self, item):
        return self.credentials[item]

    def __setitem__(self, key, value):
        self.credentials[key] = value
