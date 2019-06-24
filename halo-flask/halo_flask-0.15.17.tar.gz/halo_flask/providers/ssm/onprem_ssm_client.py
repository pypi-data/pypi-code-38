from __future__ import print_function

import configparser
import datetime
import json
import logging
import os
import time
from environs import Env
from abc import ABCMeta,abstractmethod
from halo_flask.exceptions import HaloError, CacheKeyError, CacheExpireError,HaloException
from halo_flask.providers.ssm.onprem_ssm import AbsOnPremClient
# from .logs import log_json


logger = logging.getLogger(__name__)


class OnPremClient(AbsOnPremClient):
    pass


