# -*- coding: utf-8 -*-

import faulthandler
import signal
import warnings

import pkg_resources
from ruamel import yaml

__author__ = "Uwe Schmitt"
__email__ = "uwe.schmitt@id.ethz.ch"
__version__ = pkg_resources.require("datapool")[0].version


warnings.simplefilter("ignore", yaml.error.UnsafeLoaderWarning)

faulthandler.register(signal.SIGUSR1)
