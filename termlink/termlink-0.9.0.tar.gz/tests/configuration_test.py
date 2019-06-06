"""Verifies the 'configuration.py' module."""
import os

from uuid import uuid4 as uuid

from nose.tools import eq_, ok_

from termlink.configuration import Config


def test_configuration_is_loaded():
    """Checks that the configuration is loaded"""
    configuration = Config()
    ok_(configuration)


def test_logger_is_configured():
    """Checks that the application logger has been configured"""
    configuration = Config()
    ok_(configuration.logger)


def test_logger_level():
    """The level of the logger should be INFO for the DEFAULT environment"""
    configuration = Config(environment='DEFAULT')
    logger = configuration.logger
    eq_(20, logger.level)


def test_logger_level_for_test_environment():
    """The level of the logger should be DEBUG for the TEST environment"""
    configuration = Config(environment='TEST')
    logger = configuration.logger
    eq_(10, logger.level)


def test_get_os_property():
    """OS environment variables should be exposed in the config"""
    key = str(uuid())
    value = str(uuid())
    os.environ[key] = value
    configuration = Config()
    eq_(value, configuration.get_property(key))
