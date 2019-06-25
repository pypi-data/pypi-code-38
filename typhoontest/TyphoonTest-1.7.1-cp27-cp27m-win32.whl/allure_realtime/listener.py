from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import pytest
import allure_commons
from typhoon.allure_commons import AllureCatchLogs, cli_logger


class AllurePytestLoggerListener(object):
    """This class just listens to allure and pytest hooks and dispatch
    to cli_logger module, which does the real job."""

    def __init__(self):
        self.catchlogs = AllureCatchLogs()

    @allure_commons.hookimpl
    def start_step(self, uuid, title, params):
        cli_logger.start_step(title, params)

    @allure_commons.hookimpl
    def stop_step(self, uuid, exc_type, exc_val, exc_tb):
        cli_logger.stop_step()

    @allure_commons.hookimpl
    def attach_data(self, body, name, attachment_type, extension):
        cli_logger.log("[Attachment] {}".format(name))

    # Trylast so it is after all the log capture context managers
    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_setup(self):
        with self.catchlogs:
            yield

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_call(self):
        with self.catchlogs:
            yield

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_teardown(self):
        with self.catchlogs:
            yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef, request):
        # Only creates entry on CLI
        # Probably change to call this from Afters/Befores in allure_commons
        if cli_logger is not None:
            cli_logger.start_fixture(fixturedef.argname)
        yield
        if cli_logger is not None:
            cli_logger.stop_fixture()

