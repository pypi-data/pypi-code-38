import os
import toml

from cotoba_cli import config

DIRECTORY_NAME = '.cotoba'
SESSION_FILE_NAME = 'session.toml'

HOME = os.path.expanduser('~')
COTOBA_HOME = os.path.join(HOME, DIRECTORY_NAME)


# TODO: Merge config.py.
def initialize():
    filepath = config.get_config_filepath(
        file_name=SESSION_FILE_NAME)
    directory, filename = os.path.split(filepath)
    if os.path.exists(filepath):
        return
    if not os.path.exists(directory):
        os.mkdir(directory)

    with open(filepath, 'w') as f:
        toml.dump({
            'default': {
                'email': '',
                'id_token': '',
                'access_token': '',
                'refresh_token': ''
            }
        }, f)
    os.chmod(filepath, 0o600)


def load():
    initialize()
    with open(config.get_config_filepath(
            file_name=SESSION_FILE_NAME), 'r') as f:
        return toml.load(f)


def save(email,
         id_token,
         access_token,
         refresh_token):
    filepath = config.get_config_filepath(
        file_name=SESSION_FILE_NAME)
    with open(filepath, 'w') as f:
        toml.dump({
            'default': {
                'email': email,
                'id_token': id_token,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }, f)
