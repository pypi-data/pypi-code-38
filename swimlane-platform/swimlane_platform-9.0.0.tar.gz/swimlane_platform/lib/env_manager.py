from os import path
from typing import Tuple, Iterable, Dict, List


__DELIMITER = '='


def __encode_line(key, value):
    # type: (str, str) -> str
    """
    Formats .env file line from key, value.
    :param key: Key.
    :param value: Value.
    :return: Line for .env file.
    """
    return '{key}{delimiter}{value}'.format(key=key, value=value, delimiter=__DELIMITER)


def __encode_dict(env_dict):
    # type: (Dict[str,str]) -> Iterable[str]
    """
    Generator of .env encoded strings.
    :param env_dict: Dictionary with environment values.
    """
    for key, value in env_dict.items():
        yield __encode_line(key, value)


def _parse_line(line):
    # type: (str) -> Tuple[str, str]
    """
    Makes a two value tuple from = delimited environment variable
    :param line: environment variable
    :return: key, value - tuple
    """
    spl = str(line).rstrip('\n\r ').split(__DELIMITER)
    return str(spl[0]), str('='.join(spl[1:]))


def parse_env_variables(variables):
    # type: (List[str]) -> Iterable[Tuple[str, str]]
    """
    Parses the environment variable list from Docker inspect.
    :param variables: Formatted variable list.
    """
    for variable_line in variables:
        yield _parse_line(variable_line)


def parse_env_variables_to_dict(variables):
    # type: (List[str]) -> Dict[str, str]
    """
    Parses the environment variable list from Docker inspect.
    :param variables: Formatted variable list.
    """
    return dict(parse_env_variables(variables))


def read(filename):
    # type: (str) -> Iterable[Tuple[str, str]]
    """
    Generator of key, value pairs from file.
    :param filename: File name.
    """
    with open(filename, 'r') as fs:
        for line in fs.readlines():
            yield _parse_line(line)


def read_dict(filename):
    # type: (str) -> Dict[str, str]
    """
    Reads .env file as dictionary.
    :param filename: File name.
    :return: Dictionary of environment variables.
    """
    return dict(read(filename))


def write_dict(filename, env_dict):
    # type: (str, Dict[str, str]) -> None
    """
    Writes dictionary as .env file.
    :param filename: File name.
    :param env_dict: Dictionary with environment values.
    """
    with open(filename, 'w') as fs:
        encoded_dict = [line + '\n' for line in __encode_dict(env_dict)]
        encoded_dict.sort()
        fs.writelines(encoded_dict)


def add_values_to_file(filename, env_dict):
    # type: (str, Dict[str, str]) -> None
    """
    Writes dictionary to .env file.
    :param filename: File name.
    :param env_dict: Dictionary with environment values.
    """
    if not path.exists(filename):
        write_dict(filename, env_dict)
    else:
        existing = read_dict(filename)
        for key, value in env_dict.items():
            existing[key] = value
        write_dict(filename, existing)
