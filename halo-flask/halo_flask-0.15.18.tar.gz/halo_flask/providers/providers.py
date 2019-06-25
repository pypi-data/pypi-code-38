from __future__ import print_function

import configparser
import datetime
import json
import logging
import os
import time
from abc import ABCMeta,abstractmethod

#@ TODO put_parameter should be activated only is current value is different then the existing one
#@ TODO perf activation will reload SSM if needed and refresh API table


from .ssm.aws_ssm import set_app_param_config as set_app_param_config_cld
from .ssm.aws_ssm import get_config as get_config_cld
from .ssm.aws_ssm import get_app_config as get_app_config_cld
from .ssm.onprem_ssm  import set_app_param_config as set_app_param_config_onprem
from .ssm.onprem_ssm import get_config as get_config_onprem
from .ssm.onprem_ssm import get_app_config as get_app_config_onprem
from ..settingsx import settingsx
from halo_flask.exceptions import HaloError, HaloException
from halo_flask.classes import AbsBaseClass
from halo_flask.logs import log_json


#current_milli_time = lambda: int(round(time.time() * 1000))

logger = logging.getLogger(__name__)

AWS = 'AWS'
AZURE = 'AZURE'
KUBELESS = 'KUBELESS'
ONPREM = 'ONPREM'
PROVIDERS = [AWS,AZURE,KUBELESS]


def get_provider_name():
    if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
        return AWS
    if 'KUBELESS_FUNCTION_NAME' in os.environ:
        return KUBELESS
    return ONPREM

PROVIDER = get_provider_name()
print('PROVIDER='+PROVIDER)

class Provider(AbsBaseClass):
    __metaclass__ = ABCMeta

    @abstractmethod
    def show(self): raise NotImplementedError


def get_provider():
    if PROVIDER == AWS:
        from halo_flask.providers.cloud.aws.aws import AwsProvider
        return AwsProvider()

################## ssm ###########################

def set_app_param_config(ssm_type, host):
    """

    :param region_name:
    :param host:
    :return:
    """
    if ssm_type == AWS:
        return set_app_param_config_cld(host)
    return set_app_param_config_onprem(host)



def get_config(ssm_type):
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist
    if ssm_type == AWS:
        return get_config_cld()
    return get_config_onprem()


def get_app_config(ssm_type):
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist
    if ssm_type == AWS:
        return get_app_config_cld()
    return get_app_config_onprem()

