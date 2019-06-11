# encoding: utf-8

import logging_helper
from future.utils import with_metaclass
from classutils import SingletonType
from classutils.decorators import class_cache_result, clear_class_cached_results
from configurationutil import RegisterConfig, cfg_params
from .._metadata import __version__, __authorshort__, __module_name__
from ..resources import templates, schema
from ._constants import HOST_CONFIG, ENDPOINT_CONFIG, API_CONFIG, ENVIRONMENT_CONFIG

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

HOSTS_TEMPLATE = templates.host_config
ENDPOINTS_TEMPLATE = templates.endpoint_config
APIS_TEMPLATE = templates.api_config
ENVIRONMENTS_TEMPLATE = templates.environment_config


class RegisterAPIConfig(RegisterConfig):

    """ RegisterAPIConfig provides registers and caches the config registration for APIConfig.

    Provided registrations:
        --> Environments
        --> APIs
        --> Hosts
        --> Endpoints

    This means they only have to be instantiated once each (increases performance).

    """

    def __init__(self):
        registrations = dict(environments=dict(config=ENVIRONMENT_CONFIG,
                                               config_type=cfg_params.CONST.yaml,
                                               template=ENVIRONMENTS_TEMPLATE,
                                               schema=schema.environment_config,
                                               upgrade_merge_template=True),
                             apis=dict(config=API_CONFIG,
                                       config_type=cfg_params.CONST.yaml,
                                       template=APIS_TEMPLATE,
                                       schema=schema.api_config,
                                       upgrade_merge_template=True),
                             hosts=dict(config=HOST_CONFIG,
                                        config_type=cfg_params.CONST.yaml,
                                        template=HOSTS_TEMPLATE,
                                        schema=schema.host_config,
                                        upgrade_merge_template=True),
                             endpoints=dict(config=ENDPOINT_CONFIG,
                                            config_type=cfg_params.CONST.yaml,
                                            template=ENDPOINTS_TEMPLATE,
                                            schema=schema.endpoint_config,
                                            upgrade_merge_template=True))

        super(RegisterAPIConfig, self).__init__(registrations=registrations)
