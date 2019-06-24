import os
import toml

DIRECTORY_NAME = '.cotoba'
CONFIG_FILE_NAME = 'config.toml'

HOME = os.path.expanduser('~')
COTOBA_HOME = os.path.join(HOME, DIRECTORY_NAME)


def get_config_filepath(file_name=CONFIG_FILE_NAME):
    os.environ.get('COTOBA_HOME') or COTOBA_HOME
    if os.environ.get('COTOBA_HOME'):
        directory = os.environ.get('COTOBA_HOME')
    else:
        directory = COTOBA_HOME

    directory = os.path.expanduser(directory)
    return os.path.join(directory, file_name)


def initialize():
    filepath = get_config_filepath()
    directory, filename = os.path.split(filepath)
    if os.path.exists(filepath):
        return
    if not os.path.exists(directory):
        os.mkdir(directory)

    with open(filepath, 'w') as f:
        toml.dump({
            'default': {
                # 'x-api-key': '',
                # 'developer-key': '',
                # 'api-key': '',
                # 'user-id': '',
                'endpoint-url': '',
                'locale': 'ja-JP',
                'authorization': ''
            }
        }, f)
    os.chmod(filepath, 0o600)


def load():
    initialize()
    with open(get_config_filepath(), 'r') as f:
        return toml.load(f)


def save(locale,
         url,
         authorization):
    filepath = get_config_filepath()

    with open(filepath, 'w') as f:
        toml.dump({
            'default': {
                # 'x-api-key': x_api_key,
                # 'developer-key': dev_key,
                # 'api-key': api_key,
                # 'user-id': user_id,
                'locale': locale,
                'endpoint-url': url,
                'authorization': authorization
            }
        }, f)
