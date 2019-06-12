# -*- coding: utf-8 -*-

"""Test module for nose tests helper"""

from j5test import NoseTests
import j5test
from j5test import SampleNoseTests
from j5test import SampleNoseTestsFailure
from j5test import Utils
from j5test import NoseRunner

def test_default_config():
    config = NoseTests.get_default_config()
    assert config.verbosity == 2
    assert config.includeExe == True

# TODO: re-enable these running under py.test when we can do it in a way that doesn't cause subsequent tests to fail

@Utils.if_check(Utils.in_nose_framework, "We can only run the tests using nose if this test tun is being done using nose")
def test_get_test_loader():
    loader = NoseTests.get_package_test_loader(j5test)
    suite = loader.loadTestsFromName('.')
    assert suite.countTestCases() > 50
    loader = NoseTests.get_module_test_loader(SampleNoseTests)
    suite = loader.loadTestsFromName(SampleNoseTests.__name__)
    assert suite.countTestCases() == 1
    loader = NoseTests.get_named_module_test_loader(SampleNoseTests.__file__)
    suite = loader.loadTestsFromName(SampleNoseTests.__name__)
    assert suite.countTestCases() == 1

@Utils.if_check(Utils.in_nose_framework, "We can only run the tests using nose if this test tun is being done using nose")
def test_run_tests_works():
    loader = NoseTests.get_module_test_loader(SampleNoseTests)
    suite = loader.loadTestsFromName(SampleNoseTests.__name__)
    assert NoseTests.run_tests(suite=suite)

@Utils.if_check(Utils.in_nose_framework, "We can only run the tests using nose if this test tun is being done using nose")
def test_run_tests_fails_on_error():
    loader = NoseTests.get_module_test_loader(SampleNoseTestsFailure)
    suite = loader.loadTestsFromName(SampleNoseTestsFailure.__name__)
    assert suite.countTestCases() == 1
    assert not NoseTests.run_tests(suite=suite)
    assert NoseTests.get_nose_test_name()

