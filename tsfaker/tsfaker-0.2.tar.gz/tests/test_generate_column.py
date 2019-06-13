from datetime import datetime

import numpy as np
import pytest

from tsfaker.generator import column
from tsfaker import tstype

nrows_sample = [0, 1, 7, 100]


@pytest.mark.parametrize('nrows', nrows_sample)
def test_generate_string(nrows):
    # Given
    column_generator = column.String(nrows=nrows)

    # When
    array = column_generator.get_2d_array()

    # Then
    assert (nrows, 1) == array.shape
    assert np.issubdtype(array.dtype, np.unicode_)


@pytest.mark.parametrize('nrows', nrows_sample)
def test_generate_integer(nrows):
    # Given
    column_generator = column.Integer(nrows)

    # When
    array = column_generator.get_2d_array()

    # Then
    assert (nrows, 1) == array.shape
    assert np.issubdtype(array.dtype, np.int64)


@pytest.mark.parametrize('nrows', nrows_sample)
def test_generate_float(nrows):
    # Given
    column_generator = column.Number(nrows)

    # When
    array = column_generator.get_2d_array()

    # Then
    assert (nrows, 1) == array.shape
    assert np.issubdtype(array.dtype, np.number)


@pytest.mark.parametrize('nrows', nrows_sample)
def test_generate_datetime(nrows):
    # Given
    column_generator = column.Datetime(nrows)

    # When
    array = column_generator.get_2d_array()

    # Then
    assert (nrows, 1) == array.shape
    assert np.issubdtype(array.dtype, np.unicode_)
    for _, value in np.ndenumerate(array):
        assert len(value) == 19
        datetime.strptime(value, tstype.ISO8601_DATETIME_PATTERN)


@pytest.mark.parametrize('nrows', nrows_sample)
def test_generate_date(nrows):
    # Given
    column_generator = column.Date(nrows)

    # When
    array = column_generator.get_2d_array()

    # Then
    assert (nrows, 1) == array.shape
    assert np.issubdtype(array.dtype, np.unicode_)
    for _, value in np.ndenumerate(array):
        datetime.strptime(value, tstype.ISO8601_DATE_PATTERN)


@pytest.mark.parametrize('nrows', nrows_sample)
def test_generate_year_month(nrows):
    # Given
    column_generator = column.Yearmonth(nrows)

    # When
    array = column_generator.get_2d_array()

    # Then
    assert (nrows, 1) == array.shape
    assert np.issubdtype(array.dtype, np.unicode_)
    for _, value in np.ndenumerate(array):
        datetime.strptime(value, tstype.YEAR_MONTH_PATTERN)


@pytest.mark.parametrize('nrows', nrows_sample)
def test_generate_year(nrows):
    # Given
    column_generator = column.Year(nrows)

    # When
    array = column_generator.get_2d_array()

    # Then
    assert (nrows, 1) == array.shape
    assert np.issubdtype(array.dtype, np.unicode_)
    for _, value in np.ndenumerate(array):
        datetime.strptime(value, tstype.YEAR_PATTERN)
