#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Global configuration options expressed in environment variables."""
from os import getenv
from os.path import expanduser, join

CONFIG_FILE = getenv('METADATA_CONFIG', join(
    expanduser('~'), '.pacifica-metadata', 'config.ini'))
CHERRYPY_CONFIG = getenv('METADATA_CPCONFIG', join(
    expanduser('~'), '.pacifica-metadata', 'cpconfig.ini'))
