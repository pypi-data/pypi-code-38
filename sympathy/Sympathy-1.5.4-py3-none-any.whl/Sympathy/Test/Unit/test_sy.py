# coding: utf8
# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import json
import os
import subprocess
import unittest
import sys
import tempfile
import re
import shutil
import six

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
RESOURCE_DIR = os.path.join(TEST_DIR, os.pardir, os.pardir, 'Gui', 'Resources')
FQ_ERROR_CODES_PATH = os.path.join(RESOURCE_DIR, 'error_codes.json')
SY_LIBRARY_PATH = os.path.normpath(
    os.path.join(TEST_DIR, os.pardir, os.pardir, 'Library'))
sys.path.append(os.path.join(SY_LIBRARY_PATH, 'Library'))
sys.path.append(os.path.join(SY_LIBRARY_PATH, 'Common'))
sys.path.append(TEST_DIR)
fs_encoding = sys.getfilesystemencoding()

import run_workflow as run_workflow_

from sympathy.platform import qt_compat
QtCore = qt_compat.QtCore


with open(FQ_ERROR_CODES_PATH) as error_codes_file:
    ERROR_CODES = json.load(error_codes_file)


def run_workflow(args, disable_output):
    """
    Returns a function which runs the workflow as required by nosetest's
    generator interface.
    The function will have its description attribute set to the name of the
    workflow. This will be presented as the test name by nosetest.
    """
    kwargs = {}

    if disable_output:
        kwargs['stdout'] = open(os.devnull, 'w')
        kwargs['stderr'] = subprocess.STDOUT

    run_workflow_.run_workflow(args, **kwargs)()


class TestSyBase(unittest.TestCase):
    def setUp(self):
        pass

    def _run_sy_with_arg(self, arg, expect_error, disable_output=True):
        err = None
        returncode = 0
        try:
            run_workflow(arg, disable_output or expect_error)
            err = not expect_error
        except subprocess.CalledProcessError as e:
            err = expect_error
            returncode = e.returncode
        self.assertIsNotNone(err)
        self.assertTrue(err)
        return returncode


class TestSy(TestSyBase):
    slow = 1

    def test_no_argument(self):
        returncode = self._run_sy_with_arg([], expect_error=False)
        self.assertEqual(ERROR_CODES['success']['code'], returncode)

    def test_missing_workflow_file(self):
        returncode = self._run_sy_with_arg(
            ['this_is_not_a_file_that_should_exist.syx'], expect_error=True)
        self.assertEqual(ERROR_CODES['no_such_file']['code'], returncode)

    def test_invalid_argument(self):
        returncode = self._run_sy_with_arg(
            ['--this-is-an-invalid-argument'], expect_error=True)
        self.assertEqual(ERROR_CODES['invalid_arguments']['code'], returncode)

    def test_help_argument(self):
        returncode = self._run_sy_with_arg(['-h'], expect_error=False)
        self.assertEqual(ERROR_CODES['success']['code'], returncode)

    def test_version_argument(self):
        returncode = self._run_sy_with_arg(['-v'], expect_error=False)
        self.assertEqual(ERROR_CODES['success']['code'], returncode)

    def _inifile_test(self, flag='-I'):
        pythonpath_workingdir = os.path.join(
            TEST_DIR, 'platform', 'pythonpath')
        fq_workflow_filename = os.path.join(
            pythonpath_workingdir, 'pythonpath.syx')
        python_test_library_path = os.path.join(
            pythonpath_workingdir, 'support')
        try:
            with tempfile.NamedTemporaryFile(
                    'w', prefix='test_sy_', suffix='.ini', delete=False
            ) as inifile:
                settings = QtCore.QSettings(
                    inifile.name, QtCore.QSettings.IniFormat)
                settings.setValue(
                    'Python/python_path', python_test_library_path)
                settings.setValue('config_file_version', '1.0.0')
                settings.sync()

            commands = [fq_workflow_filename, flag, inifile.name]
            returncode = self._run_sy_with_arg(commands, expect_error=False)
            self.assertEqual(ERROR_CODES['success']['code'], returncode)

        finally:
            os.unlink(inifile.name)

    def test_inifile(self):
        self._inifile_test(flag='-I')

    # def test_extras_inifile(self):
    #     self._inifile_test(flag='-e')

    # def test_quiet(self):
    #     self.assertTrue(True)

    def test_broken_link_workflow(self):
        fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'errors', 'broken_link_parent.syx')
        returncode = self._run_sy_with_arg(
            [fq_workflow_filename], expect_error=True)
        self.assertEqual(ERROR_CODES['workflow_error']['code'], returncode)

    def test_self_referencing_workflow(self):
        fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'errors', 'link_loop.syx')
        returncode = self._run_sy_with_arg(
            [fq_workflow_filename], expect_error=True)
        self.assertEqual(ERROR_CODES['empty_workflow']['code'], returncode)

    def test_indirect_self_referencing_workflow(self):
        fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'errors', 'link_loop_indirect',
            'link_loop_a.syx')
        returncode = self._run_sy_with_arg(
            [fq_workflow_filename], expect_error=True)
        self.assertEqual(ERROR_CODES['empty_workflow']['code'], returncode)

    def test_empty_workflow(self):
        fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'errors', 'empty.syx')
        returncode = self._run_sy_with_arg(
            [fq_workflow_filename], expect_error=True)
        self.assertEqual(ERROR_CODES['empty_workflow']['code'], returncode)

    def test_workflow_with_one_invalid_and_one_valid_node(self):
        fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'errors', 'invalid.syx')
        returncode = self._run_sy_with_arg(
            [fq_workflow_filename], expect_error=True)
        self.assertEqual(ERROR_CODES['invalid_nodes']['code'], returncode)

    def test_workflow_with_node_raising_exception(self):
        fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'errors', 'exception.syx')
        returncode = self._run_sy_with_arg(
            [fq_workflow_filename], expect_error=True)
        self.assertEqual(ERROR_CODES['workflow_error']['code'], returncode)

    def test_unmatched_connection_ports_workflow(self):
        fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'errors', 'unmatched_connection_ports.syx')
        returncode = self._run_sy_with_arg(
            [fq_workflow_filename], expect_error=True)
        self.assertEqual(ERROR_CODES['invalid_nodes']['code'], returncode)

    def test_unmatched_connection_type_workflow(self):
        fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'errors', 'unmatched_connection_type.syx')
        returncode = self._run_sy_with_arg(
            [fq_workflow_filename], expect_error=True)
        self.assertEqual(ERROR_CODES['invalid_nodes']['code'], returncode)

    def test_unmatched_linked_type_workflow(self):
        fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'errors', 'unmatched_linked_type.syx')
        returncode = self._run_sy_with_arg(
            [fq_workflow_filename], expect_error=True)
        self.assertEqual(ERROR_CODES['invalid_nodes']['code'], returncode)

    def test_execute_sy_workflow_with_unicode(self):
        """
        Test of executing a workflow in a unicode path
        with a workflow name with unicode characters.

        This is implemented as a unit test to avoid filename
        transcoding issues in vc.
        """
        tempdir = tempfile.mkdtemp(u'sy_unicode')
        testdir = TEST_DIR
        if six.PY2:
            tempdir = tempdir.decode(fs_encoding)
            testdir = testdir.decode(fs_encoding)

        unicodedir = os.path.join(
            testdir, u'Workflows', u'unicode')
        tempdiru = os.path.join(tempdir, u'ö')
        ohdir = os.path.join(tempdiru, u'oh-is-swedish')
        ohdiru = os.path.join(tempdiru, u'ö-is-swedish')
        wf = os.path.join(ohdir, u'test_ö-is-swedish.syx')
        wfu = os.path.join(ohdiru, u'test_ö-is-swedish.syx')

        try:
            shutil.copytree(unicodedir, os.path.join(tempdiru))
            os.rename(os.path.join(ohdir, u'test_oh-is-swedish.syx'),
                      wf)
            os.rename(ohdir, os.path.join(tempdiru, u'ö-is-swedish'))

            if six.PY2:
                self._run_sy_with_arg([wfu.encode(fs_encoding)], False)
            else:
                self._run_sy_with_arg([wfu], False)
        finally:
            try:
                shutil.rmtree(tempdir)
            except:
                pass


class TestSyConfigFile(TestSyBase):
    slow = 1

    def setUp(self):
        self.fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'example.syx')
        self.fq_config_filename = os.path.join(
            TEST_DIR, 'Workflows', 'example_config.cfg')

        self.fq_new_workflow_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False)
        self.fq_new_workflow_file.close()
        self.fq_new_workflow_filename = self.fq_new_workflow_file.name

    def tearDown(self):
        os.unlink(self.fq_new_workflow_filename)

    def test_execute_sy_without_configfile_arg(self):
        commands = [self.fq_workflow_filename, '-C']

        returncode = self._run_sy_with_arg(commands, expect_error=True)
        self.assertEqual(
            ERROR_CODES['invalid_arguments']['code'], returncode)

    def test_execute_sy_with_config_no_output_file(self):
        commands = [self.fq_workflow_filename, '-C', self.fq_config_filename]

        returncode = self._run_sy_with_arg(commands, expect_error=False)
        self.assertEqual(ERROR_CODES['success']['code'], returncode)

    def test_execute_sy_with_config_and_workflow_outfile(self):
        commands = [self.fq_workflow_filename, '-C', self.fq_config_filename,
                    self.fq_new_workflow_filename]

        returncode = self._run_sy_with_arg(commands, expect_error=False)
        self.assertEqual(ERROR_CODES['success']['code'], returncode)

        self.assertTrue(os.path.isfile(self.fq_new_workflow_filename))

        with open(self.fq_new_workflow_filename, 'r') as new_workflow_file:
            xml_text = new_workflow_file.read()
        self.assertIsNotNone(re.search('"value":\W*0.005', xml_text))
        self.assertIsNotNone(re.search('"value":\W*0.006', xml_text))

    def test_execute_sy_with_multiple_configs_workflow_output_file(self):
        fq_config_filename2 = os.path.join(
            TEST_DIR, 'Workflows', 'example_config2.cfg')
        fq_config_filename3 = os.path.join(
            TEST_DIR, 'Workflows', 'example_config3.cfg')

        fq_config_filenames = [self.fq_config_filename, fq_config_filename2,
                               fq_config_filename3]
        commands = [self.fq_workflow_filename, '-C',
                    ','.join(fq_config_filenames),
                    self.fq_new_workflow_filename]

        returncode = self._run_sy_with_arg(commands, expect_error=False)
        self.assertEqual(ERROR_CODES['success']['code'], returncode)

        self.assertTrue(os.path.isfile(self.fq_new_workflow_filename))

        with open(self.fq_new_workflow_filename, 'r') as new_workflow_file:
            xml_text = new_workflow_file.read()
        self.assertIsNotNone(re.search('"value":\W*0.003', xml_text))
        self.assertIsNotNone(
            re.search(r'"value":\W*"\\\\hello\\u0136"', xml_text))

    def test_execute_sy_with_config_and_workflow_outfile_test_env_vars(self):
        fq_workflow_filename = os.path.join(
            TEST_DIR, 'Workflows', 'special_workflows',
            'example_env_vars.syx')
        fq_data_filename = os.path.join(
            TEST_DIR, 'Workflows', 'data', 'table', 'import_random.h5')

        fq_temp_data_filename = os.path.abspath(os.path.join(
            os.path.dirname(self.fq_new_workflow_filename),
            os.path.basename(fq_data_filename)))

        try:
            shutil.copy(fq_data_filename, fq_temp_data_filename)

            commands = [fq_workflow_filename, '-C', self.fq_config_filename,
                        self.fq_new_workflow_filename]

            returncode = self._run_sy_with_arg(commands, expect_error=False)
            self.assertEqual(ERROR_CODES['success']['code'], returncode)
        finally:
            os.unlink(fq_temp_data_filename)


if __name__ == '__main__':
    unittest.main()
