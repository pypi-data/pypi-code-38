import os
from io import StringIO
from typing import List

import numpy as np
import pytest
from goodtables import validate
from tableschema import Schema

from tsfaker import tstype
from tsfaker.generator.table import TableGenerator


def build_descriptor_from_types(types: List[str]) -> dict:
    fields = [{'name': tstype_name, 'type': tstype_name} for tstype_name in types]
    return {'fields': fields}


def test_error_empty_types():
    # Given
    types = []
    descriptor = build_descriptor_from_types(types)
    table_generator = TableGenerator(descriptor, 10)

    # When
    with pytest.raises(ValueError):
        table_generator.get_array()


tstypes_to_np_dtype = [
    ([tstype.NUMBER], np.number),
    ([tstype.NUMBER, tstype.INTEGER], np.number),
    ([tstype.INTEGER], np.int64),
    ([tstype.INTEGER, tstype.INTEGER], np.int64),
    ([tstype.DATETIME], np.unicode_),
    ([tstype.DATE], np.unicode_),
    ([tstype.NUMBER, tstype.DATE], np.unicode_),
    ([tstype.NUMBER, tstype.YEAR], np.unicode_),
    ([tstype.YEAR, tstype.DATE], np.unicode_),
    (tstype.implemented, np.unicode_),
]
test_input = [(types, nrows, np_type) for (types, np_type) in tstypes_to_np_dtype for nrows in (0, 1, 7)]


@pytest.mark.parametrize('types,nrows,np_type', test_input)
def test_generate_from_types(types, nrows, np_type):
    # Given
    descriptor = build_descriptor_from_types(types)
    print()
    print(descriptor)
    table_generator = TableGenerator(descriptor, nrows)

    # When
    array = table_generator.get_array()
    buffer = StringIO()
    table_generator.get_string(buf=buffer)

    # Then
    assert np.issubdtype(array.dtype, np_type)
    assert (nrows, len(types)) == array.shape
    print('\n' + buffer.getvalue())
    validate(buffer, schema=descriptor)


def test_generate_from_schema():
    # Given
    source = os.path.join('tests', 'schemas', 'implemented_types.json')

    # When
    schema = Schema(source)
    table_generator = TableGenerator(schema.descriptor, 10)
    buffer = StringIO()
    table_generator.get_string(buf=buffer)

    # Then
    print('\n' + buffer.getvalue())
    validate(buffer, schema=schema)
