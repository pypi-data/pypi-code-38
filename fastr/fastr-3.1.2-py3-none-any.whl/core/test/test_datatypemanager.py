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

import pytest

import fastr
import os


def teardown():
    pass


def test_guesstype_url_noextension():
    pass


def test_guesstype_url_extension():
    mhd_file_mhd = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite.mhd')
    mhd_type = fastr.types.guess_type(fastr.vfs.path_to_url(mhd_file_mhd))
    assert mhd_type is fastr.types['MetaImageFile']


def test_guesstype_path_noextension():
    pass


def test_guesstype_path_extension():
    pass


def test_guesstype_options_issubclass_typegroup():
    pass


def test_guesstype_options_value_exception():
    pass