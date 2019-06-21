#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Global static variables."""
from os import getenv
from os.path import expanduser, join

CONFIG_FILE = getenv(
    'POLICY_CONFIG',
    join(expanduser('~'), '.pacifica-policy', 'config.ini')
)
CHERRYPY_CONFIG = getenv(
    'POLICY_CPCONFIG',
    join(expanduser('~'), '.pacifica-policy', 'cpconfig.ini')
)
METADATA_CONNECT_ATTEMPTS = 40
METADATA_WAIT = 3

MATCH_VALIDATORS = {
    'project': r'[0-9]+[a-zA-Z]*',
    'user': r'[0-9]+',
    'transaction': r'[0-9]+'
}
