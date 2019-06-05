import yaml
import sys
import pathlib

from gip import logger
from gip import exceptions

LOG = logger.get_logger(__name__)


def read_yaml(path):
    """
    Parse YAML file to Python object

    :param path: path to yamlfile
    :return: python object
    """
    # TODO: Rewrite to with open
    try:
        file_stream = open(path, 'r')
    except OSError as e:
        LOG.exception(e)
    else:
        try:
            return yaml.safe_load(file_stream)
        except yaml.YAMLError as e:
            raise exceptions.ParserError(
                file=path,
                error=e)
        finally:
            file_stream.close()


def write_yaml(path, data):
    """
    Write Python object to YAML

    :param path: path to yamlfile
    """
    # TODO: Rewrite to with open
    try:
        file_stream = open(path, 'w')
    except OSError as e:
        LOG.exception(e)
    else:
        try:
            yaml.safe_dump(
                data,
                stream=file_stream,
                default_flow_style=False
            )
        except yaml.YAMLError as e:
            raise exceptions.ParserError(
                file=path,
                error=e)
        finally:
            file_stream.close()


def sysexit(code=1):
    sys.exit(code)


def sysexit_with_message(msg, code=1):
    LOG.critical(msg)
    sysexit(code)


def remove_file(path):
    """
    Remove file from disk

    :param path: path to file to remove
    """
    # TODO: fix some exception handling
    pathlib.Path(path).unlink()


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result
