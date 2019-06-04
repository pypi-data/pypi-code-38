#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Configuration reading and validation module."""
try:
    from ConfigParser import SafeConfigParser
except ImportError:  # pragma: no cover python 2 vs 3 issue
    from configparser import ConfigParser as SafeConfigParser
from pacifica.archiveinterface.globals import CONFIG_FILE


def get_config():
    """Return the ConfigParser object with defaults set."""
    configparser = SafeConfigParser()
    configparser.add_section('posix')
    configparser.set('posix', 'use_id2filename', 'false')
    configparser.add_section('hpss')
    configparser.set('hpss', 'user', 'hpss.unix')
    configparser.set('hpss', 'auth', '/var/hpss/etc/hpss.unix.keytab')
    configparser.set('hpss', 'sitename', 'example.com')
    configparser.add_section('hsm_sideband')
    configparser.set('hsm_sideband', 'sam_qfs_prefix', '/data/pacifica/test/')
    configparser.set('hsm_sideband', 'schema', 'samqfs1db')
    configparser.set('hsm_sideband', 'host', 'host')
    configparser.set('hsm_sideband', 'user', 'user')
    configparser.set('hsm_sideband', 'password', 'pass')
    configparser.set('hsm_sideband', 'port', '3306')
    configparser.read(CONFIG_FILE)
    return configparser
