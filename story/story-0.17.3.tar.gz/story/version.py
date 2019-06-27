# -*- coding: utf-8 -*-
from pkg_resources import DistributionNotFound, get_distribution

try:
    version = get_distribution('story').version
    compiler_version = get_distribution('storyscript').version
except DistributionNotFound:
    # package is not installed
    version = 'unknown'
    compiler_version = 'unknown'
