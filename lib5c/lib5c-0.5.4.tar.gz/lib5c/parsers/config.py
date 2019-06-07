"""
Module for wrappers around ConfigParser for parsing config files.
"""

import ConfigParser
import json


def parse_config(configfile, name):
    """
    Parses a section from a config file into a dict.

    Parameters
    ----------
    configfile : str
        The config file to parse.
    name : str
        The section name to parse.

    Returns
    -------
    dict
        The data.
    """
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    config.read(configfile)
    data = {key: json.loads(value) for key, value in config.items(name)}
    return data
