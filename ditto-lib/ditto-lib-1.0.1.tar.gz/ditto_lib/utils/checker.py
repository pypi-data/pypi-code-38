#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  checker.py
#  Developed in 2019 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Ditto lib import module checker
#

from ditto_lib.utils.logging import logger

def check_package(package, package_name, method_name):
    if package is None:
        logger.log('error', 'Package {} is not imported and must be installed to use {}'.format(package_name, method_name))
        raise ImportError('Package {} is not imported and must be installed to use {}'.format(package_name, method_name))