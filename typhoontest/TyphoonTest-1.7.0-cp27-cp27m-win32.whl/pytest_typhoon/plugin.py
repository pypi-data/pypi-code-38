from __future__ import print_function, division
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
import subprocess
import os
import sys

# import just for monkey patching allure
import typhoon.allure_step

import typhoon.api.hil
import typhoon.test.capture
import typhoon.api.schematic_editor
import typhoon.test.signals
import typhoon.test.harmonic
import typhoon.test.rms
import typhoon.test.sources

from typhoon.pytest_typhoon import decorators
from typhoon.pytest_typhoon.typhoon_test_ide import TyphoonTestPlugin

import pytest
import logging


test_executor_name = "test_executor_tests.py"


logger = logging.getLogger(__name__)
# Warnings also should be logged with level WARNING
logging.captureWarnings(True)


### General Pytest hooks/plugins ###

def pytest_addoption(parser):
    parser.addoption("--open-allure", action="store_true",
                     help="Automatically open allure interactive report")

    parser.addoption("--msg_proxy_path",
                     help="Path of proxy file")

    parser.addoption("--no-compilation", action="store_true",
                     help="Value for no_compilation fixture (should be implemented in test code to skip compilation)")


def pytest_ignore_collect(path, config):
    path = str(path)
    if os.path.isfile(path):
        dir = os.path.dirname(path)
    elif os.path.isdir(path):
        dir = os.path.abspath(os.path.join(path, ".."))

    files = os.listdir(dir)
    if test_executor_name not in os.path.basename(path) and test_executor_name in files:
        return True


# Special assertion message rewriting, more readable
def pytest_assertrepr_compare(op, left, right):
    if op == "==":
        if isinstance(left, typhoon.test.signals.impl.AnalysisResult) and isinstance(right, bool):
            return ["Analysis result for", "'{}'".format(left.title), "is {}, expected {}.".format(left.result, right)]
        if isinstance(right, typhoon.test.signals.impl.AnalysisResult) and isinstance(left, bool):
            return ["Analysis result for", "'{}'".format(right.title), "is {}, expected {}.".format(right.result, left)]

### Stop and Plot on Fail ###

# Still needs more thought:
# - What if other tests use the same simulation run?
# - What if other tests use the same capture run? We need to be able to get intermediate data without stoping capture.
#def pytest_exception_interact(node, call, report):
#    logger.info("Exception ocurred, stoping simulation and getting capture results if still in progress.")
#    with warnings.catch_warnings():
#        if typhoon.test.capture.capture_running():
#            try:
#                if typhoon.api.hil.capture_in_progress():
#                    typhoon.api.hil.stop_capture()
#                    typhoon.test.capture.get_capture_results()
#                typhoon.api.hil.stop_simulation()
#            except Exception as e:
#                logger.error("Exception on get_capture_results_on_fail: {}".format(e))


#def pytest_assertion_pass(config, orig, expl):
#    allure.log("[Assertion Passed] {}".format(orig))
#    if expl != orig:
#        allure.log("[Assertion Details] {}".format(expl))


### Test Info Fixture ###

@pytest.fixture
def test_info(request):
    info = {
        "test_id": request.node.name,
        "test_name": request.node.originalname,
        "alluredir": request.config.getoption("--alluredir"),
    }
    return info


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    config._typhoon = PytestTyphoon(config)
    config.pluginmanager.register(config._typhoon)
    config._typhooontestide = TyphoonTestPlugin(config)
    config.pluginmanager.register(config._typhooontestide)


def allure_cmd(alluredir):
    dir_name = os.path.basename(os.path.normpath(alluredir))
    return "open_{}.cmd".format(dir_name)


def pytest_runtestloop(session):
    alluredir = session.config.getoption("--alluredir")
    if alluredir:
        cmd_name = allure_cmd(alluredir)
        with open(cmd_name,'w') as file:
            file.write("@echo off\n")
            file.write("echo TyphoonTest pytest plugin.\n")
            file.write("echo This window should remain opened for the report browser page to work.\n")
            file.write("echo After you close the browser page you can close this window.\n")
            file.write("echo ---\n")
            file.write('"{}" -m typhoon.allure_report {}'.format(sys.executable, alluredir))


def pytest_unconfigure(config):
    typhoon = getattr(config, '_typhoon', None)
    if typhoon:
        del config._typhoon
        config.pluginmanager.unregister(typhoon)

    alluredir = config.getoption("--alluredir")
    autorun_report = config.getoption("--open-allure")
    if alluredir and autorun_report:
        cmd_name = allure_cmd(alluredir)
        subprocess.call("start {}".format(cmd_name), shell=True)


class PytestTyphoon(object):

    def __init__(self, config):
        typhoon.api.hil.set_text_mode(typhoon.api.hil.RM_SYSTEM)
        typhoon.api.hil.raise_exceptions(True)
        typhoon.api.schematic_editor.model.raise_exceptions(True)

        #plot decorators
        typhoon.test.capture.get_capture_results = decorators.allure_plot_and_attach_capture_decorator(
            typhoon.test.capture.get_capture_results)
        typhoon.test.harmonic.frequency_content = decorators.allure_plot_and_attach_fft_decorator(
            typhoon.test.harmonic.frequency_content)
        typhoon.test.sources.change_grid = decorators.plot_and_attach_grid_changes(
            typhoon.test.sources.change_grid)
        decorators.decorate_module_public_attr(typhoon.test.signals, decorators.allure_plot_and_attach_analysis_decorator, inclusion_list=["is_step", "is_constant", "is_ramp", "follows_reference", "is_first_order"])

        # Decorate and configure API - order is important here, this should come after plot decorators
        decorators.decorate_module_public_attr(typhoon.api.hil, decorators.step_with_alias_decorator, exclusion_list=[
            "clstub", "raise_exceptions", "set_debug_level", "timeout_occurred", "capture_in_progress", "get_sim_time",
            "capture_in_progress", "get_analog_signals", "get_digital_signals", "read_digital_signal", "read_analog_signal",
            "get_hw_info", "get_sim_step", "get_device_features"
        ])
        # For Schematic Editor we should decorate the Class instead of the object, otherwise when we inspect we don't have access to object instance in function arguments.
        decorators.decorate_module_public_attr(typhoon.api.schematic_editor.SchematicAPI, decorators.step_with_alias_decorator, exclusion_list=["clstub", "raise_exceptions"])
        decorators.decorate_module_public_attr(typhoon.test.capture, decorators.step_with_alias_decorator, exclusion_list=["capture_running"])
        decorators.decorate_module_public_attr(typhoon.test.signals, decorators.step_with_alias_decorator)
        decorators.decorate_module_public_attr(typhoon.test.rms, decorators.step_with_alias_decorator)
        decorators.decorate_module_public_attr(typhoon.test.harmonic, decorators.step_with_alias_decorator, inclusion_list=["thd", "frequency_content"])
        decorators.decorate_module_public_attr(typhoon.test.sources, decorators.step_with_alias_decorator, inclusion_list=["change_grid"])

