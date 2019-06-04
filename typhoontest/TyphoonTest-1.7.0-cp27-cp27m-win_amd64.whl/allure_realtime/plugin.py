from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import allure_commons

from .listener import AllurePytestLoggerListener


def cleanup_factory(plugin):
    def clean_up():
        name = allure_commons.plugin_manager.get_name(plugin)
        allure_commons.plugin_manager.unregister(name=name)
    return clean_up


def pytest_addoption(parser):
    parser.getgroup("reporting").addoption('--no-allure-cli-logs',
                                           action="store_true",
                                           dest="no_allure_cli_logs",
                                           help="Disable Allure real time command line interface logging")


def pytest_configure(config):
    no_cli_logs = config.option.no_allure_cli_logs
    if not no_cli_logs:
        allure_pytest_logger_listener = AllurePytestLoggerListener()
        config.pluginmanager.register(allure_pytest_logger_listener)
        allure_commons.plugin_manager.register(allure_pytest_logger_listener)
        config.add_cleanup(cleanup_factory(allure_pytest_logger_listener))
