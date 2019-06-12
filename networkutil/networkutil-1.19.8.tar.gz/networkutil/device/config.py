# encoding: utf-8

import logging_helper
from configurationutil import Configuration, cfg_params
from .._metadata import __version__, __authorshort__, __module_name__
from ..resources import templates, schema
from ._constants import DEVICE_CONFIG

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

TEMPLATE = templates.devices
SCHEMA = schema.devices


def register_device_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=DEVICE_CONFIG,
                 config_type=cfg_params.CONST.yaml,
                 template=TEMPLATE,
                 schema=SCHEMA)

    return cfg
