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

import sympy

from fastr.core.dimension import HasDimensions, Dimension, ForwardsDimensions
from fastr import exceptions


class Dimensional(HasDimensions):
    """
    Test implementation of a HasDimensions class for testing.
    """
    SIZE = (42, 1337, sympy.Symbol('X'))
    NAME = ('answer', 'l33t', 'vague')

    def __init__(self):
        self._dimensions = tuple(Dimension(x, y) for x, y in zip(self.NAME, self.SIZE))

    @property
    def dimensions(self):
        return self._dimensions


class DimensionalForwarder(ForwardsDimensions):
    """
    Test the implementation of a ForwardsDimensions class
    """
    def __init__(self, source):
        self._source = source

    @property
    def source(self):
        return self._source

    def combine_dimensions(self, dimensions):
        """
        Strip out last dimension

        :param tuple dimensions: original dimensions
        :return: modified dimensions
        """
        return dimensions[:-1]


"""
Test for the Dimension
"""
@pytest.fixture(scope="module")
def dimension_data():
    data_container = namedtuple('DataContainer', [
        'cleese',
        'cleese2',
        'palin',
        'dummy1',
        'dummy2',
        'jones',
        'unicode',
    ])

    return data_container(
        Dimension('john', 196),
        Dimension('john', 196),
        Dimension('michael', 178),
        Dimension('john', 42),
        Dimension('dummy', 196),
        Dimension('terry', sympy.Symbol('length_jones')),
        Dimension('terry\U0001F600', 173)
    )


def test_dimension_repr(dimension_data):
    assert repr(dimension_data.cleese) == '<Dimension john (196)>'
    assert repr(dimension_data.palin) == '<Dimension michael (178)>'


def test_dimension_equal(dimension_data):
    assert dimension_data.cleese == dimension_data.cleese2
    assert dimension_data.cleese != dimension_data.palin
    assert dimension_data.jones != dimension_data.palin

    # Make sure not equal functions
    assert not (dimension_data.cleese != dimension_data.cleese2)

    # Make sure partial correct dimensions do not match
    assert dimension_data.cleese != dimension_data.dummy1
    assert dimension_data.cleese != dimension_data.dummy2


def test_dimension_name(dimension_data):
    assert dimension_data.cleese.name == 'john'
    assert dimension_data.palin.name == 'michael'
    assert dimension_data.jones.name == 'terry'


def test_dimension_size(dimension_data):
    assert dimension_data.cleese.size == 196
    assert dimension_data.palin.size == 178
    assert dimension_data.jones.size == sympy.Symbol('length_jones')


def test_dimension_update(dimension_data):
    dimension_data.cleese.update_size(178)
    assert dimension_data.cleese.size == 196

    dimension_data.palin.update_size(196)
    assert dimension_data.palin.size == 196

    dimension_data.jones.update_size(sympy.Symbol('length_jones'))
    assert dimension_data.jones.size == sympy.Symbol('length_jones')

    dimension_data.jones.update_size(173)
    assert dimension_data.jones.size == 173


def test_dimension_wrong_size_type_str():
    with pytest.raises(exceptions.FastrTypeError):
        Dimension('eric', 'idle')


def test_dimension_wrong_size_type_float():
    with pytest.raises(exceptions.FastrTypeError):
        Dimension('graham', 1.88)


def test_dimension_wrong_value_size():
    with pytest.raises(exceptions.FastrValueError):
        Dimension('negative', -1)


def test_dimension_wrong_update_type(dimension_data):
    with pytest.raises(exceptions.FastrTypeError):
        dimension_data.cleese.update_size(1.96)


def test_dimension_wrong_update_value(dimension_data):
    with pytest.raises(exceptions.FastrValueError):
        dimension_data.jones.update_size(-173)


@pytest.fixture(scope="module")
def dimensional():
        return Dimensional()


def test_dimensiona_size(dimensional):
    assert dimensional.size == dimensional.SIZE


def test_dimensional_dimnames(dimensional):
    assert dimensional.dimnames == dimensional.NAME


def test_dimensional_ndims(dimensional):
    assert dimensional.ndims == 3


@pytest.fixture(scope="module")
def dimensional_forwarder(dimensional):
    return DimensionalForwarder(dimensional)

def test_dimensional_forwarder_size(dimensional, dimensional_forwarder):
    assert dimensional_forwarder.size == dimensional.SIZE[:-1]


def test_dimensional_forwarder_dimnames(dimensional, dimensional_forwarder):
    assert dimensional_forwarder.dimnames == dimensional.NAME[:-1]


def test_dimensional_forwarder_ndims(dimensional, dimensional_forwarder):
    assert dimensional_forwarder.ndims == 2
