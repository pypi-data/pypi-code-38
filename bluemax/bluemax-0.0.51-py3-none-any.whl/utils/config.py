from tornado.options import parse_command_line, parse_config_file, options
import os
import logging
import importlib

DEFAULT_FORMAT_STRING = (
    "%(asctime)s %(levelname)-6s: %(module)-11s (%(process)d|%(thread)x): %(message)s"
)


def load_config(path=None):
    """
        This extends the tornado parser to enable use in
        heroku where options are accessed through os.getenv

        Will read file at path if exists

        Will then read environment variables to override

        Will then parse command line to override

    """
    logging.basicConfig(level=logging.INFO, format=DEFAULT_FORMAT_STRING)

    if path is not None and os.path.isfile(path):
        parse_config_file(path)
        logging.info("loaded config from %s", path)

    for k in options.as_dict():
        """ danger: access of private variables """
        value = os.getenv(k)
        if value:
            name = options._normalize_name(k)
            option = options._options.get(name)
            option.parse(value)

    parse_command_line()


def extend(extension, value):
    mdl, fn = extension.split(":")
    fn = getattr(importlib.import_module(mdl), fn)
    return fn(value)
