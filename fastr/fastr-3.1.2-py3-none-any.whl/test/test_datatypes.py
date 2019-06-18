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

import pickle
import os

import pytest

import fastr
from fastr import datatypes
from fastr import exceptions

DATA_DIR = os.path.join(os.path.dirname(__file__),
                        'data')


def test_equal():
    """
    Test if the equal operator functions correct
    """
    # Test if equal operator works well
    assert datatypes.Int(42) == datatypes.Int(42)
    assert datatypes.Float(2.5) == datatypes.Float(2.5)
    assert datatypes.String('TestString') == datatypes.String('TestString')

    # Test a few wrong cases
    assert not (datatypes.Int(42) == datatypes.Int(24))
    assert not (datatypes.String('TestString') == datatypes.String('teststring'))
    assert not (datatypes.Int(42) == datatypes.Float(42))


def test_unequal():
    """
    Test if the unequal operator functions correct
    """
    # Test if equal operator works well
    assert not (datatypes.Int(42) != datatypes.Int(42))
    assert not (datatypes.Float(2.5) != datatypes.Float(2.5))
    assert not (datatypes.String('TestString') != datatypes.String('TestString'))

    # Test a few wrong cases
    assert datatypes.Int(42) != datatypes.Int(24)
    assert datatypes.String('TestString') != datatypes.String('teststring')
    assert datatypes.Int(42) != datatypes.Float(42)


def test_load_pickle():
    """
    Load some data from pickles and test it against predefined values
    """
    with open(os.path.join(DATA_DIR, 'int_42.pickle'), 'rb') as fin:
        test_int = pickle.load(fin)
    assert test_int == datatypes.Int(42)

    with open(os.path.join(DATA_DIR, 'float_pi.pickle'), 'rb') as fin:
        test_float = pickle.load(fin)
    assert test_float == datatypes.Float(3.14159265359)

    with open(os.path.join(DATA_DIR, 'enum_test.pickle'), 'rb') as fin:
        test_enum = pickle.load(fin)

    enum_type = fastr.types.create_enumtype('TestEnumSerialization',
                                            options=['fails', 'writes', 'loads'])
    assert test_enum == enum_type('loads')


def test_getstate_setstate():
    """
    Test if the getstate and set state work well
    """
    # Test some known states
    assert datatypes.Int(3).__getstate__() == ('Int', 3, None)
    assert datatypes.Float(4.2).__getstate__() == ('Float', 4.2, None)
    assert datatypes.String('test').__getstate__() == ('String', 'test', None)

    # Do a round trip
    source_int = datatypes.Int(10)
    target_int = datatypes.Int()

    target_int.__setstate__(source_int.__getstate__())
    assert source_int == target_int


def test_wrong_setstate():
    """
    Test if the TypeCheck in get/set state works correctly
    """
    test_float = datatypes.Float(42)
    test_int = datatypes.Int()
    with pytest.raises(exceptions.FastrValueError):
        test_int.__setstate__(test_float.__getstate__())


def test_round_trip_pickle():
    """
    Dump datatype objects to a pickle and rebuilt them. Verify that they are the same.
    """
    # Round trip with an Int
    test_int = datatypes.Int(7)
    test_int_rebuilt = pickle.loads(pickle.dumps(test_int))
    assert test_int == test_int_rebuilt

    # Round trip with an Enum
    enum_type = fastr.types.create_enumtype('TestEnumSerializationRoundTrip',
                                            options=['ham', 'spam', 'eggs'])
    test_enum = enum_type('eggs')
    test_enum_rebuilt = pickle.loads(pickle.dumps(test_enum))
    assert test_enum == test_enum_rebuilt


def test_raw_value():
    test_string = datatypes.String('Test string')
    assert test_string.value == test_string.raw_value


def test_validate_error():
    class WrongDataType(datatypes.URLType):
        def _validate(self):
            raise NotImplementedError("We don't like no validation!")

    test_data = WrongDataType('test')
    with pytest.raises(NotImplementedError):
        print('{} is {}'.format(test_data,
                                'valid' if test_data.valid else 'not valid'))


def test_default_validate():
    class SimpleDatatype(datatypes.BaseDataType):
        def __init__(self, value):
            super(SimpleDatatype, self).__init__(value)

    test_data = SimpleDatatype('test 123')
    print('{} is {}'.format(test_data,
                            'valid' if test_data.valid else 'not valid'))
    assert test_data.valid


def test_checksum():
    """
    Make sure some type checksums stay constant, including some duplicated
    files.
    """
    img1_path = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite.mhd')
    img2_path = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite_duplicate.mhd')
    txt1_path = os.path.join(fastr.config.mounts['example_data'], 'add_ints', 'values')
    txt2_path = os.path.join(fastr.config.mounts['example_data'], 'add_ints', 'values_duplicate')

    assert datatypes.Int(42).checksum() == 'a1d0c6e83f027327d8461063f4ac58a6'
    assert datatypes.Float('13.37').checksum() == '4cf47d0124912e13713bc06b31971c5e'
    assert datatypes.String('Test123').checksum() == '68eacb97d86f0c4621fa2b0e17cabd8c'
    assert datatypes.TxtFile(txt1_path).checksum() == 'b742e35f18a05cf2ebac5e3f0a91599b'
    assert datatypes.TxtFile(txt2_path).checksum() == 'b742e35f18a05cf2ebac5e3f0a91599b'
    assert datatypes.MetaImageFile(img1_path).checksum() == 'eabeb2aca52d581f701070eb84c1934b'
    assert datatypes.MetaImageFile(img2_path).checksum() == 'eabeb2aca52d581f701070eb84c1934b'
