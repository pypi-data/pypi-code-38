from typing import *
import os
from pathlib import Path
from fifteenrock.lib import util

FR_CREDENTIALS_PATH = 'FR_CREDENTIALS_PATH'
FR_FILE_NAME = 'fifteenrock.json'


def default_config_path(credentials_file=FR_FILE_NAME):
    return Path(os.getcwd()) / credentials_file


def get_credentials(credentials: Dict, credentials_path: str):
    if credentials:
        return credentials
    if credentials_path:
        credentials_path = Path(credentials_path)
    path = credentials_path or get_default_config_path_if_exists() or environment_path() or python_path_file()
    if path:
        return util.read_json(path)['default']
    else:
        msg = f"""
        Credentials Path not provided. Either 
        - provide "credentials_path" or
        - put the json file in your current working directory or
        - set the environment variable {FR_CREDENTIALS_PATH} 
        - Store the file in your PYTHONPATH
        """
        raise ValueError(msg)


def get_default_config_path_if_exists():
    default_path = default_config_path()
    if default_path.is_file():
        return default_path


def environment_path():
    import os
    config_path = os.environ.get(FR_CREDENTIALS_PATH)

    if config_path:
        return Path(config_path)
    else:
        return None


def python_path_file():
    python_path = os.environ.get('PYTHONPATH')
    if python_path:
        possible_path = Path(os.path.join(python_path, FR_FILE_NAME))
        if possible_path.is_file():
            return possible_path
        else:
            return None
    else:
        return None


def determine_credentials(path: Path = None) -> Dict:
    _path = path or default_config_path()
    return util.read_json(_path)['default']


def read_config(config_file: str) -> Dict:
    if config_file:
        return util.read_json(Path(config_file))
    else:
        return dict()


def default_file_path(relative_file_path: str, cwd: str = None) -> Union[str, None]:
    cwd = cwd or os.getcwd()
    p = os.path.join(cwd, relative_file_path)
    from pathlib import Path
    my_file = Path(p)
    if not my_file.is_file():
        return None
    else:
        return p
