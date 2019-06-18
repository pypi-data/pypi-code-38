# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import tempfile
import random
import shutil
import string

import fastr
from fastr import exceptions
from fastr.resources import ioplugins

import pytest


class TestVFS:

    def setup(self):
        fastr.log.info('Setup')
        """ Setup the test environment for the vfs tests. """
        # We assume there is a tmp mount. (It should be tested).
        # Generate a file in the tmp mount.
        self.dir = os.path.join(fastr.config.mounts['tmp'], '_test')
        if os.path.exists(self.dir):
            fastr.log.warning('Cleaning up existing temporary test directory {}'.format(self.dir))
            shutil.rmtree(self.dir)
        os.makedirs(self.dir)
        fastr.log.info('Using temporary directory {}'.format(self.dir))
        if not os.path.isdir(self.dir):
            fastr.log.critical('Temporary directory not available!')

        self.source_dir = os.path.join(self.dir, 'source')
        os.mkdir(self.source_dir)
        self.destination_dir = os.path.join(self.dir, 'destination')
        os.mkdir(self.destination_dir)

        self.handle, self.absfilename = tempfile.mkstemp(dir=self.source_dir)
        self.filename = os.path.basename(self.absfilename)
        self.niigz_handle, self.niigz_absfilename = tempfile.mkstemp(dir=self.source_dir, suffix='.nii.gz')
        self.niigz_filename = os.path.basename(self.niigz_absfilename)

        fastr.log.info('Created {} and {}'.format(self.absfilename, self.niigz_absfilename))
        if not os.path.exists(self.absfilename):
            fastr.log.critical('Source file {} does not exist!'.format(self.absfilename))
        if not os.path.exists(self.niigz_absfilename):
            fastr.log.critical('Source file {} does not exist!'.format(self.niigz_absfilename))

    def teardown(self):
        """ Tear down the test environment for the vfs tests. """
        # Delete the generated temporary file
        shutil.rmtree(self.dir)

    def random_unique_string(self, length=8, existing=None):
        """ Return a random alpha-numeric string with a certain length. """
        s = ''.join([random.choice(string.ascii_letters + string.digits) for ch in range(length)])
        if existing is not None and s in existing:
            s = self.random_unique_string(length, existing)
        return s

    def test_url_to_path(self):
        assert fastr.vfs.url_to_path('vfs://tmp/_test/source/{}'.format(self.filename)) == self.absfilename

    def test_path_to_url(self):
        assert fastr.vfs.path_to_url(self.absfilename) == 'vfs://tmp/_test/source/{}'.format(self.filename)

    def test_url_to_path_unknown_scheme(self):
        # Get a random sequence of strings to get a non existing scheme.
        s = self.random_unique_string(length=5, existing=list(ioplugins.keys()))
        with pytest.raises(exceptions.FastrUnknownURLSchemeError):
            fastr.vfs.url_to_path("{}://tmp/blaat.nii.gz".format(s))

    def test_url_to_path_unknown_mount(self):
        # Get a random sequence of strings to get a non existing scheme.
        m = self.random_unique_string(length=5, existing=list(fastr.config.mounts.keys()))
        with pytest.raises(exceptions.FastrMountUnknownError):
            fastr.vfs.url_to_path("vfs://{}/blaat.nii.gz".format(m))

    def test_path_to_url_unknown_mount(self):
        # Get a random sequence of strings to get a non existing scheme.
        m = self.random_unique_string(length=5, existing=list(fastr.config.mounts.keys()))
        with pytest.raises(exceptions.FastrMountUnknownError):
            fastr.vfs.path_to_url("/{}/blaat.nii.gz".format(m))
