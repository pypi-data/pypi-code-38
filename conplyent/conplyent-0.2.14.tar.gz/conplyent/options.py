'''
:File: options.py
:Author: Jayesh Joshi
:Email: jayeshjo1@utexas.edu
'''

import os
import json
import logging
import click
from datetime import datetime
from pathlib import Path

from ._general import logger, os_name


def save_logs():
    '''
    If this method is called, any console output from conplyent will be saved
    onto a local folder. Conplyent options uses a local folder at either
    %appdata%/conplyent/conplyent.json or ~/.conplyent/conplyent.json
    directory depending on user's os. These options can be editted using
    :meth:`options.edit_options`.

    Currently, these options include: log_dir and max_logs.

    * log_dir specifies the directory which conplyent will save logs
    * max_logs determines how many logs conplyent will store. If next log will
        exceed this value, will delete the oldest log.
    '''
    options_path, log_info = _create_options()\

    if(not(log_info)):
        log_info = _dump_defaults(options_path)

    log_dir = log_info["logging_dir"][os_name()]
    try:
        user_name = os.getlogin()
    except OSError:
        user_name = "root"
    log_path = Path(log_dir.format(user_name=user_name))
    log_path.mkdir(parents=True, exist_ok=True)

    # Remove logs if > max_logs
    existing_logs = sorted(log_path.glob(r"*.log"), key=lambda k: k.stat().st_ctime)
    if(len(existing_logs) >= log_info["max_logs"]):
        existing_logs[0].unlink()

    time_tag = datetime.now().strftime("--%Y-%m-%d--%H-%M-%S")
    fileHandler = logging.FileHandler("{}/{}".format(str(log_path), "conplyent_{}.log".format(time_tag)))
    fileHandler.setFormatter(logging.Formatter("<%(asctime)s> [%(threadName)-10.10s][%(levelname)-5.5s] %(message)s"))
    logger.addHandler(fileHandler)


def edit_options(revert=False):
    '''
    Allows users to edit the system local conplyent options.

    :param revert: If specified, will revert conplyent options to defaults.
    :type revert: bool
    '''
    options_path, log_info = _create_options()

    if(revert):
        _dump_defaults(options_path)
    else:
        new_options = _edit_each(log_info, "Conplyent")

        with open("{}/{}".format(str(options_path), "conplyent.json"), "w") as constants:
            log_info = json.dump(new_options, constants, indent=4)


def _create_options():
    options_path = _options_path()
    if(not(os.path.exists("{}/{}".format(str(options_path), "conplyent.json")))):
        options_path.mkdir(parents=True, exist_ok=True)
        return options_path, _dump_defaults(options_path)
    else:
        with open("{}/{}".format(str(options_path), "conplyent.json"), "r") as constants:
            log_info = json.load(constants)
        return options_path, log_info


def _options_path():
    if(os_name() == "windows"):
        option_path = Path("{}/conplyent".format(os.environ["appdata"]))
    elif(os_name() == "linux"):
        option_path = Path("/home/{username}/.conplyent")
    else:
        raise NotImplementedError("Conplyent has not been released for this OS")
    return option_path


def _dump_defaults(options_path):
    default_options = {
        "logging_dir": {
            "windows": "c:/Users/{user_name}/Documents/conplyent/logs",
            "linux": "/home/{user_name}/conplyent/logs"
        },
        "max_logs": 10
    }

    with open("{}/{}".format(str(options_path), "conplyent.json"), "w") as file:
        json.dump(default_options, file, indent=4)

    return default_options


def _edit_each(param, string):
    result = {}
    for key, value in param.items():
        if(type(value) is dict):
            result[key] = _edit_each(value, "{}:{}".format(string, key))
        else:
            result[key] = click.prompt("{}:{}".format(string, key), default=value)
    return result
