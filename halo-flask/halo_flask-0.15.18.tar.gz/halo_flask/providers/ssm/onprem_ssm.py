from __future__ import print_function

import configparser
import datetime
import json
import logging
import os
import time
from environs import Env
from abc import ABCMeta,abstractmethod
from halo_flask.exceptions import HaloError, CacheKeyError, CacheExpireError,HaloException,NoLocalSSMClass,NoLocalSSMModule
from halo_flask.classes import AbsBaseClass
# from .logs import log_json
from halo_flask.base_util import BaseUtil
from halo_flask.settingsx import settingsx
settings = settingsx()

current_milli_time = lambda: int(round(time.time() * 1000))

logger = logging.getLogger(__name__)

client = None
full_config_path,short_config_path = BaseUtil.get_env()

class AbsOnPremClient(AbsBaseClass):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_parameters_by_path(self,Path,Recursive,WithDecryption): raise NotImplementedError("NotImplemented get_parameters_by_path in OnPremClient")

    @abstractmethod
    def put_parameter(self,Name,Value,Type,Overwrite): raise NotImplementedError("NotImplemented put_parameter in OnPremClient")


def get_onprem_client()->AbsOnPremClient:
    if settings.ONPREM_SSM_CLASS_NAME:
        class_name = settings.ONPREM_SSM_CLASS_NAME
    else:
        raise NoLocalSSMClass("no ONPREM_SSM_CLASS_NAME")
    if settings.ONPREM_SSM_MODULE_NAME:
        module = settings.ONPREM_SSM_MODULE_NAME
    else:
        raise NoLocalSSMModule("no ONPREM_SSM_MODULE_NAME")
    import importlib
    module = importlib.import_module(module)
    class_ = getattr(module, class_name)
    instance = class_()
    return instance

def get_client():
    """

    :param region_name:
    :return:
    """
    logger.debug("get_client")
    global client
    if not client:
        client = get_onprem_client()
    return client



# ALWAYS use json value in parameter store!!!

class Cache(AbsBaseClass):
    expiration = 0
    items = None


DEFAULT_EXPIRY = 3 * 60 * 1000;  # default expiry is 3 mins


def load_cache(config, expiryMs=DEFAULT_EXPIRY):
    """

    :param config:
    :param expiryMs:
    :return:
    """
    if config is None:
        raise HaloError('you need to provide a non-empty config')

    if (expiryMs <= 0):
        raise HaloError('you need to specify an expiry (ms) greater than 0, or leave it undefined')

    # the below uses the captured closure to return an object with a gettable
    # property per config key that on invoke:
    #  * fetch the config values and cache them the first time
    #  * thereafter, use cached values until they expire
    #  * otherwise, try fetching from SSM parameter store again and cache them

    now = datetime.datetime.now()
    cache = Cache()
    cache.expiration = current_milli_time() + expiryMs
    cache.items = config

    logger.debug('refreshed cache')
    return cache


class MyConfig(AbsBaseClass):
    def __init__(self, cache, path):
        """
        Construct new MyApp with configuration
        :param config: application configuration
        """
        self.cache = cache
        self.path = path

    def get_param(self, key):
        """

        :param key:
        :return:
        """
        now = current_milli_time()
        if now <= self.cache.expiration:
            if key in self.cache.items:
                return self.cache.items[key]
            else:
                raise CacheKeyError("no key in cache:" + key)
        else:
            self.cache = get_cache(self.region_name, self.path)
            if key in self.cache.items:
                return self.cache.items[key]
        raise CacheExpireError("cache expired")


def load_config(ssm_parameter_path):
    """
    Load configparser from config stored in SSM Parameter Store
    :param ssm_parameter_path: Path to app config in SSM Parameter Store
    :return: ConfigParser holding loaded config
    """
    configuration = configparser.ConfigParser()
    try:
        # Get all parameters for this app
        param_details = get_client().get_parameters_by_path(
            Path=ssm_parameter_path,
            Recursive=False,
            WithDecryption=True
        )

        logger.debug(str(ssm_parameter_path) + "=" + str(param_details))
        # Loop through the returned parameters and populate the ConfigParser
        if 'Parameters' in param_details and len(param_details.get('Parameters')) > 0:
            for param in param_details.get('Parameters'):
                param_path_array = param.get('Name').split("/")
                section_position = len(param_path_array) - 1
                section_name = param_path_array[section_position]
                config_values = json.loads(param.get('Value'))
                config_dict = {section_name: config_values}
                logger.debug("Found configuration: " + str(config_dict))
                configuration.read_dict(config_dict)

    except HaloException as e:
        logger.error("Encountered a client error loading config from SSM:" + str(e))
    except json.decoder.JSONDecodeError as e:
        logger.error("Encountered a json error loading config from SSM:" + str(e))
    except Exception as e:
        logger.error("Encountered an error loading config from SSM:" + str(e))
    finally:
        return configuration


def set_param_config(region_name, key, value):
    """

    :param region_name:
    :param key:
    :param value:
    :return:
    """
    ssm_parameter_path = full_config_path + '/' + key
    return set_config(region_name, ssm_parameter_path, value)


def set_app_param_config(host):
    """

    :param region_name:
    :param host:
    :return:
    """
    ssm_parameter_path = short_config_path + '/' + BaseUtil.get_func()
    if host:
        url = "https://" + host + "/" + BaseUtil.get_stage()
    else:
        url = host
    value = '{"url":"' + str(url) + '"}'
    logger.debug("ssm:" + value)
    return set_config(ssm_parameter_path, value)


def set_config(ssm_parameter_path, value):
    """
    Load configparser from config stored in SSM Parameter Store
    :param ssm_parameter_path: Path to app config in SSM Parameter Store
    :return: ConfigParser holding loaded config
    """
    try:
        # set parameters for this app

        json.loads(value)
        ret = get_client().put_parameter(
            Name=ssm_parameter_path,
            Value=value,
            Type='String',
            Overwrite=True
        )

        logger.debug(str(full_config_path) + "=" + str(ret))
        return True
    except HaloException as e:
        logger.error("Encountered a client error setting config from SSM:" + str(e))
    except json.decoder.JSONDecodeError as e:
        logger.error("Encountered a json error setting config from SSM" + str(e))
    except Exception as e:
        logger.error("Encountered an error setting config from SSM:" + str(e))
    return False


def get_cache(path):
    """

    :param region_name:
    :param path:
    :return:
    """
    logger.debug("get_cache")
    config = load_config(path)
    cache = load_cache(config)
    return cache


def get_config():
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist
    logger.debug("Loading config and creating new MyConfig..." + full_config_path)
    cache = get_cache(full_config_path)
    myconfig = MyConfig(cache, full_config_path)
    logger.debug("MyConfig is " + str(cache.items._sections))
    return myconfig


def get_app_config():
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist
    logger.debug("Loading app config and creating new AppConfig..." + short_config_path)
    cache = get_cache(short_config_path)
    appconfig = MyConfig(cache, short_config_path)
    logger.debug("AppConfig is " + str(cache.items._sections))
    return appconfig
