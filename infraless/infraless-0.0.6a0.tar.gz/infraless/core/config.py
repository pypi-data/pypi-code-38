#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml

from ..core.exc import InfralessError

INFRALESS_CONST_CONFIG_FILENAME = '.ilconfig'


def ilassert_ilconfig_exists():
    if INFRALESS_CONST_CONFIG_FILENAME not in os.listdir(os.curdir):
        raise InfralessError('No config file found')


def validate_ilconfig():
    ilassert_ilconfig_exists()
    with open(INFRALESS_CONST_CONFIG_FILENAME, 'r') as stream:
        try:
            print(yaml.safe_load(stream))
        except yaml.YAMLError:
            raise InfralessError('Invalid .ilconfig found.')
    pass
