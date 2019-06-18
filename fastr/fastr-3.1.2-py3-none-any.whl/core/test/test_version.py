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

from collections import namedtuple

import pytest

from fastr import exceptions
from fastr.core.version import Version


@pytest.fixture(scope="module")
def version_data():
    data_container = namedtuple('DataContainer', [
        'data1',
        'data2',
        'data3',
        'data4',
        'data5',
        'data6',
        'data7',
        'data8',
    ])

    return data_container(
        Version(),
        Version(0, 0, None, 'b', 42),
        Version((1, 2)),
        Version([3, 4, [5, 6], 'beta', 3, None, '-']),
        Version('0.1-r3'),
        Version('1.2.3.4.5.6.7-beta8_with_suffix'),
        Version([3, 4, (5, 6), 'beta', 3, None, '-']),
        Version('3.3.2'),
    )


def test_data(version_data):
    assert version_data.data1 == (0, 0, None, None, None, None, None)
    assert version_data.data2 == (0, 0, None, 'b', 42, None, None)
    assert version_data.data3 == (1, 2, None, None, None, None, None)
    assert version_data.data4 == (3, 4, (5, 6), 'beta', 3, None, '-')
    assert version_data.data5 == (0, 1, None, 're', 3, '', '-')
    assert version_data.data6 == (1, 2, (3, 4, 5, 6, 7), 'beta', 8, '_with_suffix', '-')
    assert version_data.data7 == (3, 4, (5, 6), 'beta', 3, None, '-')
    assert version_data.data8 == (3, 3, (2,), None, None, '', None)


def test_string(version_data):
    assert str(version_data.data1) == '0.0'
    assert str(version_data.data2) == '0.0b42'
    assert str(version_data.data3) == '1.2'
    assert str(version_data.data4) == '3.4.5.6-beta3'
    assert str(version_data.data5) == '0.1-r3'
    assert str(version_data.data6) == '1.2.3.4.5.6.7-beta8_with_suffix'
    assert str(version_data.data7) == '3.4.5.6-beta3'
    assert str(version_data.data8) == '3.3.2'


def test_major(version_data):
    assert version_data.data1.major == 0
    assert version_data.data2.major == 0
    assert version_data.data3.major == 1
    assert version_data.data4.major == 3
    assert version_data.data5.major == 0
    assert version_data.data6.major == 1
    assert version_data.data7.major == 3
    assert version_data.data8.major == 3


def test_minor(version_data):
    assert version_data.data1.minor == 0
    assert version_data.data2.minor == 0
    assert version_data.data3.minor == 2
    assert version_data.data4.minor == 4
    assert version_data.data5.minor == 1
    assert version_data.data6.minor == 2
    assert version_data.data7.minor == 4
    assert version_data.data8.minor == 3


def test_extra(version_data):
    assert version_data.data1.extra is None
    assert version_data.data2.extra is None
    assert version_data.data3.extra is None
    assert version_data.data4.extra == (5, 6)
    assert version_data.data5.extra is None
    assert version_data.data6.extra == (3, 4, 5, 6, 7)
    assert version_data.data7.extra == (5, 6)
    assert version_data.data8.extra == (2,)


def test_extra_string(version_data):
    assert version_data.data1.extra_string == ''
    assert version_data.data2.extra_string == ''
    assert version_data.data3.extra_string == ''
    assert version_data.data4.extra_string == '.5.6'
    assert version_data.data5.extra_string == ''
    assert version_data.data6.extra_string == '.3.4.5.6.7'
    assert version_data.data7.extra_string == '.5.6'
    assert version_data.data8.extra_string == '.2'


def test_wrong_version_int():
    # Cannot use int, should raise an Error
    with pytest.raises(exceptions.FastrVersionInvalidError):
        Version(2)


def test_wrong_version_float():
    # Cannot use float, should raise an Error
    with pytest.raises(exceptions.FastrVersionInvalidError):
        Version(3.0)


def test_wrong_version_invalid_str():
    with pytest.raises(exceptions.FastrVersionInvalidError):
        Version('test123')


def test_wrong_version_list_too_long():
    with pytest.raises(exceptions.FastrVersionInvalidError):
        Version(list(range(10)))

