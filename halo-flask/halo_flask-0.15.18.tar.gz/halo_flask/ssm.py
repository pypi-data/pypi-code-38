from __future__ import print_function

import configparser
import datetime
import json
import logging
import os
import time

#@ TODO put_parameter should be activated only is current value is different then the existing one
#@ TODO perf activation will reload SSM if needed and refresh API table

from .providers.providers import set_app_param_config as set_app_param_config_provider
from .providers.providers import get_config as get_config_provider
from .providers.providers import get_app_config as get_app_config_provider


from .exceptions import HaloError, CacheKeyError, CacheExpireError

# from .logs import log_json


#current_milli_time = lambda: int(round(time.time() * 1000))

logger = logging.getLogger(__name__)

client = None


def set_app_param_config(ssm_type, host):
    """

    :param region_name:
    :param host:
    :return:
    """

    return set_app_param_config_provider(ssm_type,host)



def get_config(ssm_type):
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist

    return get_config_provider(ssm_type)


def get_app_config(ssm_type):
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist

    return get_app_config_provider(ssm_type)
