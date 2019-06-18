import os
import shutil
import configparser
from . import paths as path_helpers


MANIFEST = "__manifest__.py"
LEGACY_MANIFEST = ("__addons_manifest__.py",)


def get_project_manifest():
    """
    Read and parse out the __addons_manifest.py config that sits in the root
    directory of module collection folders.

    This will throw an exception and exit the CLI program / make program all
    together if the file cannot be read properly or the file cannot be parsed
    (exec) properly.

    :raises Exception:
    :return {dict}:
    """
    paths = path_helpers.Paths()

    try:
        f = open(paths.base(MANIFEST), "r").read()
        return eval(f)
    except Exception as e:
        for legacy_format in LEGACY_MANIFEST:
            if os.path.isfile(paths.base(legacy_format)):
                shutil.move(paths.base(legacy_format), paths.base(MANIFEST))
                try:
                    f = open(paths.base(MANIFEST), "r").read()
                    return eval(f)
                except Exception as e:
                    continue

        raise Exception(
            "There was a problem processing your __manifest__.py file for the project. Make sure it exists and is in a valid format."
            + "\n"
        )


def _parse_config(path):
    """
    Helper method to parse a configuration from a file path.

    :param path {str}: The path to the configuration file
    :return {config.configparser.ConfigParser|NoneType}:
        Returns None if the file cannot be found or if there is an error
        in parsing the configuration file. Otherwise the full configuration
        object is return after performing a `read` on the file.
    """
    try:
        if not os.path.isfile(path):
            return None

        configuration = configparser.ConfigParser(allow_no_value=True)
        configuration.read(path)

        return configuration
    except Exception as e:
        print(str(e))
        return None


def init():
    global setup_calls
    global pipe_dev_null
    global paths
    global standard_env_path
    global odoo_env_path
    global config
    global odoo_env_config

    setup_calls = {}
    pipe_dev_null = path_helpers.pipe_dev_null
    paths = path_helpers.Paths()
    standard_env_path = paths.base(".env")
    odoo_env_path = paths.base(".container/env/odoo/odoo.env")
    config = load_standard_config(standard_env_path)
    odoo_env_config = load_odoo_env_config(odoo_env_path)


def setup_called():
    global setup_calls
    pid = os.getpid()
    ppid = os.getppid()

    setup_calls[ppid] = setup_calls[ppid] + 1 if ppid in setup_calls else 1
    setup_calls[pid] = setup_calls[pid] + 1 if pid in setup_calls else 1


def can_setup():
    global setup_calls
    pid = os.getpid()
    ppid = os.getppid()

    return ppid not in setup_calls and pid not in setup_calls


def load_standard_config(env_path):
    """
    Used to load a standard configuration.

    :param env_path {str}: Path to the configuration file
    :return {config.configparser.ConfigParser|NoneType}:
        Returns None if the file cannot be found or if there is an error
        in parsing the configuration file. Otherwise the full configuration
        object is return after performing a `read` on the file.
    """
    return _parse_config(env_path)


def load_odoo_env_config(env_path):
    """
    Used to load an odoo specific configuration.

    :param env_path {str}: Path to the configuration file
    :return {config.configparser.ConfigParser|NoneType}:
        Returns None if the file cannot be found or if there is an error
        in parsing the configuration file. Otherwise the full configuration
        object is return after performing a `read` on the file.
    """
    return _parse_config(env_path)
