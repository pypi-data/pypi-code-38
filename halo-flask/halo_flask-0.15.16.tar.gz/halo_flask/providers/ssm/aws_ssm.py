from __future__ import print_function

import configparser
import datetime
import json
import logging
import os
import time
from environs import Env
import boto3
from botocore.exceptions import ClientError

from halo_flask.exceptions import HaloError, CacheKeyError, CacheExpireError
from halo_flask.classes import AbsBaseClass
# from .logs import log_json
from halo_flask.base_util import BaseUtil
from halo_flask.settingsx import settingsx
settings = settingsx()

current_milli_time = lambda: int(round(time.time() * 1000))

logger = logging.getLogger(__name__)

# Initialize boto3 client at global scope for connection reuse
client = None
region_name = None
full_config_path,short_config_path = BaseUtil.get_env()

def get_client(region_name):
    """

    :param region_name:
    :return:
    """
    logger.debug("get_client")
    global client
    if not client:
        client = boto3.client('ssm', region_name=region_name)
    return client

def get_region():
    logger.debug("get_region")
    global region_name
    if not region_name:
        region_name = settings.AWS_REGION
    return region_name

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
    def __init__(self, cache, path, region_name):
        """
        Construct new MyApp with configuration
        :param config: application configuration
        """
        self.cache = cache
        self.path = path
        self.region_name = region_name

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


def load_config(region_name, ssm_parameter_path):
    """
    Load configparser from config stored in SSM Parameter Store
    :param ssm_parameter_path: Path to app config in SSM Parameter Store
    :return: ConfigParser holding loaded config
    """
    configuration = configparser.ConfigParser()
    try:
        # Get all parameters for this app
        param_details = get_client(region_name).get_parameters_by_path(
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

    except ClientError as e:
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
    region_name = get_region()
    ssm_parameter_path = short_config_path + '/' + BaseUtil.get_func()
    if host:
        url = "https://" + host + "/" + BaseUtil.get_stage()
    else:
        url = host
    value = '{"url":"' + str(url) + '"}'
    print("app ssm_parameter_path:" + ssm_parameter_path+" value:"+value)
    return set_config(region_name, ssm_parameter_path, value)


def set_config(region_name, ssm_parameter_path, value):
    """
    Load configparser from config stored in SSM Parameter Store
    :param ssm_parameter_path: Path to app config in SSM Parameter Store
    :return: ConfigParser holding loaded config
    """
    try:
        # set parameters for this app

        json.loads(value)
        ret = get_client(region_name).put_parameter(
            Name=ssm_parameter_path,
            Value=value,
            Type='String',
            Overwrite=True
        )

        logger.debug(str(full_config_path) + "=" + str(ret))
        return True
    except ClientError as e:
        logger.error("Encountered a client error setting config from SSM:" + str(e))
    except json.decoder.JSONDecodeError as e:
        logger.error("Encountered a json error setting config from SSM" + str(e))
    except Exception as e:
        logger.error("Encountered an error setting config from SSM:" + str(e))
    return False


def get_cache(region_name, path):
    """

    :param region_name:
    :param path:
    :return:
    """
    logger.debug("get_cache")
    config = load_config(region_name, path)
    cache = load_cache(config)
    return cache


def get_config():
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist
    region_name = get_region()
    print("region_name:"+str(region_name))
    logger.debug("Loading config and creating new MyConfig..." + full_config_path+",AWS_REGION="+region_name)
    cache = get_cache(region_name, full_config_path)
    myconfig = MyConfig(cache, full_config_path, region_name)
    logger.debug("MyConfig is " + str(cache.items._sections))
    return myconfig


def get_app_config():
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist
    region_name = BaseUtil.get_func_region()
    logger.debug("Loading app config and creating new AppConfig..." + short_config_path+",AWS_REGION="+region_name)
    cache = get_cache(region_name, short_config_path)
    appconfig = MyConfig(cache, short_config_path, region_name)
    logger.debug("AppConfig is " + str(cache.items._sections))
    return appconfig
