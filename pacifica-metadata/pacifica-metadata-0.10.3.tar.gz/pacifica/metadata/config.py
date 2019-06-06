#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Configuration reading and validation module."""
import logging
from os import getenv
try:
    from ConfigParser import SafeConfigParser
except ImportError:  # pragma: no cover python 2 vs 3 issue
    from configparser import ConfigParser as SafeConfigParser
from pacifica.metadata.globals import CONFIG_FILE


def get_config():
    """
    Return the ConfigParser object with defaults set.

    Currently metadata API doesn't work with SQLite the queries are
    too complex and it only is supported with MySQL and PostgreSQL.
    """
    configparser = SafeConfigParser()
    configparser.add_section('database')
    configparser.set('database', 'connect_attempts', getenv(
        'DATABASE_CONNECT_ATTEMPTS', '10'))
    configparser.set('database', 'connect_wait', getenv(
        'DATABASE_CONNECT_WAIT', '20'))
    configparser.set('database', 'debug_logging', getenv(
        'DATABASE_DEBUG_LOGGING', 'False'))
    configparser.set('database', 'peewee_url', getenv(
        'PEEWEE_URL', 'postgresql://pacifica:metadata@localhost:5432/pacifica_metadata'))
    configparser.add_section('notifications')
    configparser.set('notifications', 'disabled', getenv(
        'NOTIFICATIONS_DISABLED', 'False'))
    configparser.set('notifications', 'url', getenv(
        'NOTIFICATIONS_URL', 'http://127.0.0.1:8070/receive'))
    configparser.set('notifications', 'ingest_eventtype', getenv(
        'NOTIFICATIONS_INGEST_EVENT_TYPE', 'org.pacifica.metadata.ingest'))
    configparser.set('notifications', 'ingest_source', getenv(
        'NOTIFICATIONS_INGEST_SOURCE', 'http://metadata.pacifica.org/transactions?_id={_id}'))
    configparser.set('notifications', 'ingest_eventid', getenv(
        'NOTIFICATIONS_INGEST_EVENTID', 'metadata.ingest.{_id}'))
    configparser.set('notifications', 'orm_eventtype', getenv(
        'NOTIFICATIONS_ORM_EVENT_TYPE', 'org.pacifica.metadata.orm'))
    configparser.set('notifications', 'orm_source', getenv(
        'NOTIFICATIONS_ORM_SOURCE', 'http://metadata.pacifica.org/{object_name}'))
    configparser.set('notifications', 'orm_eventid', getenv(
        'NOTIFICATIONS_ORM_EVENTID', 'metadata.orm.{object_name}.{uuid}'))
    configparser.set('notifications', 'doientry_eventtype', getenv(
        'NOTIFICATIONS_DOIENTRY_EVENT_TYPE', 'org.pacifica.metadata.doientry'))
    configparser.set('notifications', 'doientry_source', getenv(
        'NOTIFICATIONS_DOIENTRY_SOURCE', 'http://metadata.pacifica.org/doientry'))
    configparser.set('notifications', 'doientry_eventid', getenv(
        'NOTIFICATIONS_DOIENTRY_EVENTID', 'metadata.doi.{uuid}'))
    configparser.set('notifications', 'doiupdate_eventtype', getenv(
        'NOTIFICATIONS_DOIUPDATE_EVENT_TYPE', 'org.pacifica.metadata.doiupdate'))
    configparser.set('notifications', 'doiupdate_source', getenv(
        'NOTIFICATIONS_DOIUPDATE_SOURCE', 'http://metadata.pacifica.org/doientry?doi={doi}'))
    configparser.set('notifications', 'doiupdate_eventid', getenv(
        'NOTIFICATIONS_DOIUPDATE_EVENTID', 'metadata.doi.{doi}.{uuid}'))
    configparser.read(CONFIG_FILE)
    return configparser


if get_config().getboolean('database', 'debug_logging'):  # pragma: no cover used for debugging
    LOGGER = logging.getLogger('peewee')
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(logging.StreamHandler())
