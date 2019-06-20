
from unittest import TestSuite
from importlib import import_module
import inspect

from termcolor import colored

from .eztestcase import EZTestCase


class EZTestSuite(TestSuite):

    OUTPUT_PROMPT = "* "

    def __init__(self, name, module_name):
        TestSuite.__init__(self, [])
        self.name = name
        self.test_classes = list()
        suite_module = import_module(module_name)
        for (name, obj) in inspect.getmembers(suite_module):
            if inspect.isclass(obj) and issubclass(obj, EZTestCase) and obj is not EZTestCase:
                self.test_classes.append(obj)

    def run(self, result, debug=False):
        self.output_prerun_info()
        TestSuite.run(self, result, debug)
        self.output_postrun_info()

    def add_test_class(self, tc_class):
        self.test_classes.append(tc_class)

    def init_test_instances(self, eztest):
        for tc_class in self.test_classes:
            instance = tc_class(eztest)
            self.addTest(instance)

    def output_prerun_info(self):
        self.suite_print('Running test suite "%s"~>' % colored(self.name, 'cyan'))

    def output_postrun_info(self):
        print('')
        self.suite_print('Done!')

    def suite_print(self, string):
        print((colored(self.OUTPUT_PROMPT, 'yellow') + string))
