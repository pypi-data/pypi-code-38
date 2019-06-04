#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Global configuration options expressed in environment variables."""
from os import getenv
from os.path import expanduser, join

CONFIG_FILE = getenv('ARCHIVEINTERFACE_CONFIG', join(
    expanduser('~'), '.pacifica-archiveinterface', 'config.ini'))
CHERRYPY_CONFIG = getenv('ARCHIVEINTERFACE_CPCONFIG', join(
    expanduser('~'), '.pacifica-archiveinterface', 'cpconfig.ini'))
