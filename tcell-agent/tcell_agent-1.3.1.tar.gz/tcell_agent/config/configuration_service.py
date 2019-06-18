from __future__ import unicode_literals
from __future__ import print_function

import json
import os
import os.path
import traceback

from future.backports.urllib.parse import urlsplit

from tcell_agent.config.configuration import TCellAgentConfiguration, \
     get_config, set_config
from tcell_agent.config.unknown_options import get_unknown_options
from tcell_agent.loggers.module_logger import ModuleLogger
from tcell_agent.loggers.python_logger import PythonLogger


def get_logger(config):
    return ModuleLogger(__name__,
                        PythonLogger(config.logging_options,
                                     config.log_directory))


class TCellAgentConfigurationException(Exception):
    pass


def filter_commentlines(json_data):
    """
    Removes full line comments from json to provide trivial
    support for commenting. Does not remove end of line
    comments.
    :param json_data: A json text string
    :return: json text without comments
    """
    return "\n".join(l for l in json_data.split("\n") if not l.strip().startswith("//"))


def validate_url(url, error):
    try:
        urlsplit(url)
    except Exception:
        raise TCellAgentConfigurationException("{}: {}".format(error, url))


def get_config_filename_that_exists(config_filename,
                                    backup_check_config_filename):
    if os.path.isfile(config_filename):
        return config_filename
    if os.path.isfile(backup_check_config_filename):
        return backup_check_config_filename

    return None


def load_config_file(config, filename):
    config_json = None

    config_filename = os.path.abspath(os.environ.get("TCELL_AGENT_CONFIG", filename))
    backup_check_config_filename = os.path.abspath(os.path.join(config.tcell_home, filename))

    config.config_filename = get_config_filename_that_exists(config_filename,
                                                             backup_check_config_filename)

    if not config.config_filename:
        get_logger(config).info(
            ("Configuration file not found (checked: {} and {}), "
             "will rely on environmental variables.").format(config_filename,
                                                             backup_check_config_filename)
        )
        return config_json

    if not os.access(config.config_filename, os.R_OK):
        print("tCell.io Agent: [Error] Permission denied opening config file: {}.".format(config.config_filename))
        get_logger(config).error("Permission denied for file '{}'".format(config.config_filename))
        return config_json

    try:
        with open(config.config_filename, "r") as data_file:
            try:
                json_data = filter_commentlines(data_file.read())
                config_json = json.loads(json_data)
            except ValueError as ve:
                print("tCell.io Agent: [Error] Could not parse json in config file: {}.".format(config.config_filename))
                traceback.print_exc()
                get_logger(config).error("Could not parse json in config file: {}.".format(config.config_filename))
                get_logger(config).exception(ve)
    except OSError as ose:
        print("tCell.io Agent: Exception opening configuration file: {}".format(ose))
        traceback.print_exc()
        get_logger(config).error("tCell.io Agent: Exception loading configuration file: {}".format(ose))
        get_logger(config).exception(ose)

    return config_json


def validate_config(config, config_json):
    validate_url(config.tcell_input_url, "Could not parse tcell_input_url")
    validate_url(config.tcell_api_url, "Could not parse tcell_api_url")

    if config_json:
        if "version" not in config_json:
            print("tCell.io Agent: {} is missing version".format(config.config_filename))
            get_logger(config).error("tCell.io Agent: {} is missing version".format(config.config_filename))
        elif config_json.get("version") != 1:
            print("tCell.io Agent: {} is incorrect version".format(config.config_filename))
            get_logger(config).error("tCell.io Agent: {} is incorrect version".format(config.config_filename))

    if not config.app_id or not config.api_key:
        raise TCellAgentConfigurationException(
            "Application ID and API Key must be set by configuration file or environmental variables."
        )

    map(get_logger(config).warn, get_unknown_options(config_json))


def init_config():
    if get_config():
        return get_config()

    config = TCellAgentConfiguration()
    config_json = load_config_file(config, "tcell_agent.config")
    if config_json:
        config.read_config(config_json)
    config.load_env_vars()

    validate_config(config, config_json)
    set_config(config)

    return config
