#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
from .console import EndlessConsole, Console
import logging
from . import config
import importlib

class Test():
    """
    Handle test operations
    """
    COVERAGE_PATH = '/opt/raspiot/.coverage'

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__endless_command_running = False
        self.__endless_command_return_code = 0
        self.__module_version = None
        if not os.path.exists(self.COVERAGE_PATH):
            os.makedirs(self.COVERAGE_PATH)

    def __console_callback(self, stdout, stderr):
        self.logger.info((stdout if stdout is not None else '') + (stderr if stderr is not None else ''))

    def __console_end_callback(self, return_code, killed):
        self.__endless_command_running = False
        self.__endless_command_return_code = return_code

    def __get_module_version(self, module_name):
        if self.__module_version:
            return self.__module_version

        try:
            module_ = importlib.import_module(u'raspiot.modules.%s.%s' % (module_name, module_name))
            module_class_ = getattr(module_, module_name.capitalize())
            self.__module_version = module_class_.MODULE_VERSION
            return self.__module_version
        except:
            self.logger.exception('Unable to get module version. Is module valid?')
            return None

    def __get_coverage_file(self, module_name, module_version):
        """
        Return coverage file

        Args:
            module_name (string): module name
            module_version (string): module version

        Returns:
            string: coverage file
        """
        cov_file = os.path.join(self.COVERAGE_PATH, '%s.%s.cov' % (module_name, module_version))
        self.logger.debug('Coverage file = %s' % cov_file)
        return cov_file

    def __get_module_tests_path(self, module_name):
        """
        Return module path

        Args:
            module_name (string): module name

        Returns:
            string: module tests path
        """
        return '%s/%s/tests' % (config.MODULES_SRC, module_name)

    def module_test_coverage(self, module_name, missing=False):
        """
        Display module coverage

        Args:
            module_name (string): module name
            missing (bool): display missing statements (default False)
        """
        #checking module path
        path = os.path.join(config.MODULES_SRC, module_name, 'tests')
        if not os.path.exists(path):
            self.logger.error('Specified module "%s" does not exist' % (module_name))
            return False

        module_version = self.__get_module_version(module_name)
        if module_version is None:
            return False

        coverage_file = self.__get_coverage_file(module_name, module_version)
        if not os.path.exists(coverage_file):
            self.logger.error('No coverage file found. Did tests run ?')
            return False

        cmd = """
cd "%s"
COVERAGE_FILE=%s coverage report %s
        """ % (self.__get_module_tests_path(module_name), self.__get_coverage_file(module_name, module_version), '-m' if missing else '')
        c = Console()
        res = c.command(cmd)
        if res['error'] or res['killed']:
            self.logger.error('Error during command execution: %s' % (res['sterr']))
            return False

        self.logger.info('\n'.join(res['stdout']))

        return True

    def module_test(self, module_name, display_coverage=False):
        """
        Execute module unit tests

        Args:
            module_name (string): module name
            display_coverage (bool): display coverage report (default False)
        """
        #checking module path
        path = os.path.join(config.MODULES_SRC, module_name, 'tests')
        if not os.path.exists(path):
            self.logger.error('Specified module "%s" does not exist' % (module_name))
            return False

        #create module coverage path
        module_version = self.__get_module_version(module_name)
        if module_version is None:
            return False

        self.logger.info('Running unit tests...')
        cmd = """
cd "%s"
COVERAGE_FILE=%s coverage run --omit="/usr/local/lib/python2.7/*","test_*","../backend/*Event.py" --source="../backend" --concurrency=thread test_*.py
        """ % (self.__get_module_tests_path(module_name), self.__get_coverage_file(module_name, module_version))
        self.logger.debug('Test cmd: %s' % cmd)
        self.__endless_command_running = True
        c = EndlessConsole(cmd, self.__console_callback, self.__console_end_callback)
        c.start()

        while self.__endless_command_running:
            time.sleep(0.25)

        #display coverage report
        if display_coverage:
            self.logger.debug('Display coverage')
            self.module_test_coverage(module_name)

        self.logger.debug('Return code: %s' % self.__endless_command_return_code)
        if self.__endless_command_return_code!=0:
            return False

        return True

