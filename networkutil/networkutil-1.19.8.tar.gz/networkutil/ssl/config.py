# encoding: utf-8

import os
import logging_helper
from configurationutil import Configuration, cfg_params, CfgItems, CfgItem
from .._metadata import __version__, __authorshort__, __module_name__
from ..resources import templates, schema
from .constants import SSL_CONFIG, SSLConstant, SSL_DATA_DIR

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

TEMPLATE = templates.ssl
SCHEMA = schema.ssl


def get_file_path(fn,
                  ext,
                  pth=SSL_DATA_DIR):
    return os.path.join(pth,
                        u'{f}.{e}'.format(f=fn,
                                          e=ext))


def get_config_file_path(fn,
                         ext):

    cfg = register_ssl_config()
    path = os.path.join(cfg.data_path_unversioned,
                        SSL_DATA_DIR)

    return os.path.join(path,
                        u'{f}.{e}'.format(f=fn,
                                          e=ext))


def register_ssl_config():
    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=SSL_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=SCHEMA)

    return cfg


class SSLCertificate(CfgItem):
    pass


class SSLCertificates(CfgItems):

    def __init__(self):
        super(SSLCertificates, self).__init__(cfg_fn=register_ssl_config,
                                              cfg_root=SSL_CONFIG,
                                              key_name=SSLConstant.name,
                                              item_class=SSLCertificate)
