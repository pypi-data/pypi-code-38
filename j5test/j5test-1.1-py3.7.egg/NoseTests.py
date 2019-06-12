# -*- coding: utf-8 -*-

"""Utility functions to help with working with nose
with our default configuration (i.e. something like py.test)"""

from nose import config
from nose import loader
from nose import core
from nose import plugins

import os
import re
import sys
import inspect

def get_default_config(**kwargs):
    """Returns a configuration file set up with our default settings
    Extra arguments can be passed in through kwargs"""
    kwargs.setdefault("verbosity", 2)
    kwargs.setdefault("includeExe", True)
    kwargs.setdefault("testMatch", re.compile("^[Tt]est"))
    if "plugins" not in kwargs:
        kwargs["plugins"] = plugins.DefaultPluginManager()
    return config.Config(**kwargs)

def get_named_module_test_loader(path_name):
    """Takes a base module name, and returns a loader already loaded with tests, ready for a TestRunner
    e.g. "ld = get_package_test_loader('x.y.z')" will get all tests under x.y.z"""
    workingDir = os.path.dirname(os.path.abspath(path_name))
    basename = os.path.basename(path_name)
    cfg = get_default_config(workingDir=workingDir)
    cfg.testNames = [basename]
    return loader.TestLoader(config=cfg)

def get_module_test_loader(base_module):
    """Takes a base module, and returns a loader already loaded with tests, ready for a TestRunner
    e.g. "import j5test.test_NoseTests ; ld = get_package_test_loader(j5)" will get all tests under j5test.test_NoseTests"""
    workingDir = os.path.dirname(base_module.__file__)
    basename = os.path.basename(base_module.__file__)
    cfg = get_default_config(workingDir=workingDir)
    cfg.testNames = [basename]
    return loader.TestLoader(config=cfg)

def get_package_test_loader(base_module):
    """Takes a base package, and returns a loader already loaded with tests, ready for a TestRunner
    e.g. "import j5 ; ld = get_package_test_loader(j5)" will get all tests under j5"""
    workingDir = os.path.dirname(base_module.__file__)
    cfg = get_default_config(workingDir=workingDir)
    return loader.TestLoader(config=cfg)

def run_tests(loader=None, **kwargs):
    """Given a TestLoader, runs the tests"""
    # simple way of passing through loader with default config from above
    if loader:
        kwargs["testLoader"] = loader
    if "config" not in kwargs and loader:
        kwargs["config"] = loader.config
    # don't exit by default
    if "exit" not in kwargs:
        kwargs["exit"] = False
    # don't use sys.argv automatically
    if "argv" not in kwargs:
        kwargs["argv"] = [sys.argv[0]]
    program = core.TestProgram(**kwargs)
    return program.success

def get_nose_test_name():
    """To be called from setUp or tearDown - can get the nose test currently running"""
    setup_frame = inspect.currentframe().f_back
    # Now back to the test case
    testcase_frame = setup_frame.f_back.f_back
    # Now look for self
    if 'self' not in testcase_frame.f_locals:
        raise ValueError("Frame %r does not seem to be the test case - nose upgrade?" % testcase_frame)
    return testcase_frame.f_locals['self'].id()

