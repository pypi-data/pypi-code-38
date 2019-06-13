#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module for validating data with the library pandas."""

import os
import warnings
import datetime

import numpy
import pandas


__author__ = 'Markus Englund'
__license__ = 'MIT'
__version__ = '0.5.0'


warnings.filterwarnings('default', category=DeprecationWarning)


class ValidationWarning(Warning):
    pass


def _datetime_to_string(series, format='%Y-%m-%d'):
    """
    Convert datetime values in a pandas Series to strings.
    Other values are left as they are.

    Parameters
    ----------
    series : pandas.Series
        Values to convert.
    format : str
        Format string for datetime type. Default: '%Y-%m-%d'.

    Returns
    -------
    converted : pandas.Series
    """
    converted = series.copy()
    datetime_mask = series.apply(type).isin(
        [datetime.datetime, pandas.Timestamp])
    if datetime_mask.any():
        converted[datetime_mask] = (
            series[datetime_mask].apply(lambda x: x.strftime(format)))
    return converted.where(datetime_mask, series)


def _numeric_to_string(series, float_format='%g'):
    """
    Convert numeric values in a pandas Series to strings.
    Other values are left as they are.

    Parameters
    ----------
    series : pandas.Series
        Values to convert.
    float_format : str
        Format string for floating point number. Default: '%g'.

    Returns
    -------
    converted : pandas.Series
    """
    converted = series.copy()
    numeric_mask = (
        series.apply(lambda x: numpy.issubdtype(type(x), numpy.number)) &
        series.notnull())
    if numeric_mask.any():
        converted[numeric_mask] = (
            series[numeric_mask].apply(lambda x: float_format % x))
    return converted.where(numeric_mask, series)


def _get_error_messages(masks, error_info):
    """
    Get list of error messages.

    Parameters
    ----------
    masks : list
        List of pandas.Series with masked errors.
    error_info : dict
        Dictionary with error messages corresponding to different
        validation errors.
    """
    msg_list = []
    for key, value in masks.items():
        if value.any():
            msg_list.append(error_info[key])
    return msg_list


def _get_return_object(masks, values, return_type):
    mask_frame = pandas.concat(masks, axis='columns')
    if return_type == 'mask_frame':
        return mask_frame
    elif return_type == 'mask_series':
        return mask_frame.any(axis=1)
    elif return_type == 'values':
        return values.where(~mask_frame.any(axis=1))
    else:
        raise ValueError('Invalid return_type')


def mask_nonconvertible(
        series, to_datatype, datetime_format=None, exact_date=True):
    """
    Return a boolean same-sized object indicating whether values
    cannot be converted.

    Parameters
    ----------
    series : pandas.Series
        Values to check.
    to_datatype : str
        Datatype to which values should be converted. Available values
        are 'numeric' and 'datetime'.
    datetime_format : str
        strftime to parse time, eg '%d/%m/%Y', note that '%f' will parse
        all the way up to nanoseconds. Optional.
    exact_date : bool
        - If True (default), require an exact format match.
        - If False, allow the format to match anywhere in the target string.
    """
    if to_datatype == 'numeric':
        converted = pandas.to_numeric(series, errors='coerce')
    elif to_datatype == 'datetime':
        converted = pandas.to_datetime(
            series, errors='coerce', format=datetime_format, exact=exact_date)
    else:
        raise ValueError(
            'Invalid \'to_datatype\': {}'
            .format(to_datatype))  # pragma: no cover
    notnull = series.copy().notnull()
    mask = notnull & converted.isnull()
    return mask


def to_datetime(
        arg, dayfirst=False, yearfirst=False, utc=None, box=True,
        format=None, exact=True, coerce=None, unit='ns',
        infer_datetime_format=False):
    """
    Convert argument to datetime and set nonconvertible values to NaT.

    This function calls :func:`~pandas.to_datetime` with ``errors='coerce'``
    and issues a warning if values cannot be converted.
    """
    try:
        converted = pandas.to_datetime(
            arg, errors='raise', dayfirst=dayfirst, yearfirst=yearfirst,
            utc=utc, box=box, format=format, exact=exact)
    except ValueError:
        converted = pandas.to_datetime(
            arg, errors='coerce', dayfirst=dayfirst, yearfirst=yearfirst,
            utc=utc, box=box, format=format, exact=exact)
        if isinstance(arg, pandas.Series):
            warnings.warn(
                '{}: value(s) not converted to datetime set as NaT'
                .format(repr(arg.name)), ValidationWarning, stacklevel=2)
        else:  # pragma: no cover
            warnings.warn(
                'Value(s) not converted to datetime set as NaT',
                ValidationWarning, stacklevel=2)
    return converted


def to_numeric(arg):
    """
    Convert argument to numeric type and set nonconvertible values
    to NaN.

    This function calls :func:`~pandas.to_numeric` with ``errors='coerce'``
    and issues a warning if values cannot be converted.
    """
    try:
        converted = pandas.to_numeric(arg, errors='raise')
    except ValueError:
        converted = pandas.to_numeric(arg, errors='coerce')
        if isinstance(arg, pandas.Series):
            warnings.warn(
                '{}: value(s) not converted to numeric set as NaN'
                .format(repr(arg.name)), ValidationWarning, stacklevel=2)
        else:  # pragma: no cover
            warnings.warn(
                'Value(s) not converted to numeric set as NaN',
                ValidationWarning, stacklevel=2)
    return converted


def to_string(series, float_format='%g', datetime_format='%Y-%m-%d'):
    """
    Convert values in a pandas Series to strings.

    Parameters
    ----------
    series : pandas.Series
        Values to convert.
    float_format : str
        Format string for floating point number. Default: '%g'.
    datetime_format : str
        Format string for datetime type. Default: '%Y-%m-%d'

    Returns
    -------
    converted : pandas.Series
    """
    converted = _numeric_to_string(series, float_format)
    converted = _datetime_to_string(converted, format=datetime_format)
    converted = converted.astype(str)
    converted = converted.where(series.notnull(), numpy.nan)  # missing as NaN
    return converted


def validate_date(
        series, nullable=True, unique=False, min_date=None,
        max_date=None, return_type=None):
    """
    Validate a pandas Series with values of type `datetime.date`.
    Values of a different data type will be replaced with NaN prior to
    the validataion.

    Parameters
    ----------
    series : pandas.Series
        Values to validate.
    nullable : bool
        If False, check for NaN values. Default: True.
    unique : bool
        If True, check that values are unique. Default: False
    min_date : datetime.date
        If defined, check for values before min_date. Optional.
    max_date : datetime.date
        If defined, check for value later than max_date. Optional.
    return_type : str
        Kind of data object to return; 'mask_series', 'mask_frame'
        or 'values'. Default: None.
    """
    error_info = {
        'invalid_type': 'Value(s) not of type datetime.date set as NaT',
        'isnull': 'NaT value(s)',
        'nonunique': 'duplicates',
        'too_low': 'date(s) too early',
        'too_high': 'date(s) too late'}

    is_date = series.apply(lambda x: isinstance(x, datetime.date))
    masks = {}
    masks['invalid_type'] = ~is_date & series.notnull()
    to_validate = series.where(is_date)
    if nullable is not True:
        masks['isnull'] = to_validate.isnull()
    if unique:
        masks['nonunique'] = to_validate.duplicated() & to_validate.notnull()
    if min_date is not None:
        masks['too_low'] = to_validate.dropna() < min_date
    if max_date is not None:
        masks['too_high'] = to_validate.dropna() > max_date

    msg_list = _get_error_messages(masks, error_info)

    if len(msg_list) > 0:
        msg = repr(series.name) + ': ' + '; '.join(msg_list) + '.'
        warnings.warn(msg, ValidationWarning, stacklevel=2)

    if return_type is not None:
        return _get_return_object(masks, to_validate, return_type)


def validate_timestamp(
        series, nullable=True, unique=False, min_timestamp=None,
        max_timestamp=None, return_type=None):
    """
    Validate a pandas Series with values of type `pandas.Timestamp`.
    Values of a different data type will be replaced with NaT prior to
    the validataion.

    Parameters
    ----------
    series : pandas.Series
        Values to validate.
    nullable : bool
        If False, check for NaN values. Default: True.
    unique : bool
        If True, check that values are unique. Default: False
    min_timestamp : pandas.Timestamp
        If defined, check for values before min_timestamp. Optional.
    max_timestamp : pandas.Timestamp
        If defined, check for value later than max_timestamp. Optional.
    return_type : str
        Kind of data object to return; 'mask_series', 'mask_frame'
        or 'values'. Default: None.
    """
    error_info = {
        'invalid_type': 'Value(s) not of type pandas.Timestamp set as NaT',
        'isnull': 'NaT value(s)',
        'nonunique': 'duplicates',
        'too_low': 'timestamp(s) too early',
        'too_high': 'timestamp(s) too late'}

    is_timestamp = series.apply(lambda x: isinstance(x, pandas.Timestamp))
    masks = {}
    masks['invalid_type'] = ~is_timestamp & series.notnull()
    to_validate = pandas.to_datetime(series.where(is_timestamp, pandas.NaT))
    if nullable is not True:
        masks['isnull'] = to_validate.isnull()
    if unique:
        masks['nonunique'] = to_validate.duplicated() & to_validate.notnull()
    if min_timestamp is not None:
        masks['too_low'] = to_validate.dropna() < min_timestamp
    if max_timestamp is not None:
        masks['too_high'] = to_validate.dropna() > max_timestamp

    msg_list = _get_error_messages(masks, error_info)

    if len(msg_list) > 0:
        msg = repr(series.name) + ': ' + '; '.join(msg_list) + '.'
        warnings.warn(msg, ValidationWarning, stacklevel=2)

    if return_type is not None:
        return _get_return_object(masks, to_validate, return_type)


def validate_datetime(
        series, nullable=True, unique=False, min_datetime=None,
        max_datetime=None, return_type=None):
    """
    Validate a pandas Series containing datetimes.

    .. deprecated:: 0.5.0
        `validate_datetime()` will be removed in version 0.7.0.
        Use `validate_date()` or `validate_timestamp()` instead.

    Parameters
    ----------
    series : pandas.Series
        Values to validate.
    nullable : bool
        If False, check for NaN values. Default: True.
    unique : bool
        If True, check that values are unique. Default: False
    min_datetime : str
        If defined, check for values before min_datetime. Optional.
    max_datetime : str
        If defined, check for value later than max_datetime. Optional.
    return_type : str
        Kind of data object to return; 'mask_series', 'mask_frame'
        or 'values'. Default: None.
    """

    warnings.warn(
        'validate_datetime() is deprecated, use validate_date() or '
        'validate_timestamp() instead.', DeprecationWarning)

    error_info = {
        'nonconvertible': 'Value(s) not converted to datetime set as NaT',
        'isnull': 'NaT value(s)',
        'nonunique': 'duplicates',
        'too_low': 'date(s) too early',
        'too_high': 'date(s) too late'}

    if not series.dtype.type == numpy.datetime64:
        converted = pandas.to_datetime(series, errors='coerce')
    else:
        converted = series.copy()
    masks = {}
    masks['nonconvertible'] = series.notnull() & converted.isnull()
    if not nullable:
        masks['isnull'] = converted.isnull()
    if unique:
        masks['nonunique'] = converted.duplicated() & converted.notnull()
    if min_datetime is not None:
        masks['too_low'] = converted.dropna() < min_datetime
    if max_datetime is not None:
        masks['too_high'] = converted.dropna() > max_datetime

    msg_list = _get_error_messages(masks, error_info)

    if len(msg_list) > 0:
        msg = repr(series.name) + ': ' + '; '.join(msg_list) + '.'
        warnings.warn(msg, ValidationWarning, stacklevel=2)

    if return_type is not None:
        return _get_return_object(masks, converted, return_type)


def validate_numeric(
        series, nullable=True, unique=False, integer=False,
        min_value=None, max_value=None, return_type=None):
    """
    Validate a pandas Series containing numeric values.

    Parameters
    ----------
    series : pandas.Series
        Values to validate.
    nullable : bool
        If False, check for NaN values. Default: True
    unique : bool
        If True, check that values are unique. Default: False
    integer : bool
        If True, check that values are integers. Default: False
    min_value : int
        If defined, check for values below minimum. Optional.
    max_value : int
        If defined, check for value above maximum. Optional.
    return_type : str
        Kind of data object to return; 'mask_series', 'mask_frame'
        or 'values'. Default: None.
    """
    error_info = {
        'invalid_type': 'Non-numeric value(s) set as NaN',
        'isnull': 'NaN value(s)',
        'nonunique': 'duplicates',
        'noninteger': 'non-integer(s)',
        'too_low': 'value(s) too low',
        'too_high': 'values(s) too high'}

    is_numeric = series.apply(pandas.api.types.is_number)

    masks = {}
    masks['invalid_type'] = ~is_numeric & series.notnull()

    to_validate = pandas.to_numeric(series.where(is_numeric))
    if not nullable:
        masks['isnull'] = to_validate.isnull()
    if unique:
        masks['nonunique'] = to_validate.duplicated() & to_validate.notnull()
    if integer:
        noninteger_dropped = (
            to_validate.dropna() != to_validate.dropna().apply(int))
        masks['noninteger'] = pandas.Series(noninteger_dropped, series.index)
    if min_value is not None:
        masks['too_low'] = to_validate.dropna() < min_value
    if max_value is not None:
        masks['too_high'] = to_validate.dropna() > max_value

    msg_list = _get_error_messages(masks, error_info)

    if len(msg_list) > 0:
        msg = repr(series.name) + ': ' + '; '.join(msg_list) + '.'
        warnings.warn(msg, ValidationWarning, stacklevel=2)

    if return_type is not None:
        return _get_return_object(masks, to_validate, return_type)


def validate_string(
        series, nullable=True, unique=False,
        min_length=None, max_length=None, case=None, newlines=True,
        trailing_whitespace=True, whitespace=True, matching_regex=None,
        non_matching_regex=None, whitelist=None, blacklist=None,
        return_type=None):
    """
    Validate a pandas Series with strings. Non-string values
    will be converted to strings prior to validation.

    Parameters
    ----------
    series : pandas.Series
        Values to validate.
    nullable : bool
        If False, check for NaN values. Default: True.
    unique : bool
        If True, check that values are unique. Default: False.
    min_length : int
        If defined, check for strings shorter than
        minimum length. Optional.
    max_length : int
        If defined, check for strings longer than
        maximum length. Optional.
    case : str
        Check for a character case constraint. Available values
        are 'lower', 'upper' and 'title'. Optional.
    newlines : bool
        If False, check for newline characters. Default: True.
    trailing_whitespace : bool
        If False, check for trailing whitespace. Default: True.
    whitespace : bool
         If False, check for whitespace. Default: True.
    matching_regex : str
        Check that strings matches some regular expression. Optional.
    non_matching_regex : str
        Check that strings do not match some regular expression. Optional.
    whitelist : list
        Check that values are in `whitelist`. Optional.
    blacklist : list
        Check that values are not in `blacklist`. Optional.
    return_type : str
        Kind of data object to return; 'mask_series', 'mask_frame'
        or 'values'. Default: None.
    """

    error_info = {
        'invalid_type': 'Non-string value(s) set as NaN',
        'isnull': 'NaN value(s)',
        'nonunique': 'duplicates',
        'too_short': 'string(s) too short',
        'too_long': 'string(s) too long',
        'wrong_case': 'wrong case letter(s)',
        'newlines': 'newline character(s)',
        'trailing_space': 'trailing whitespace',
        'whitespace': 'whitespace',
        'regex_mismatch': 'mismatch(es) for "matching regular expression"',
        'regex_match': 'match(es) for "non-matching regular expression"',
        'not_in_whitelist': 'string(s) not in whitelist',
        'in_blacklist': 'string(s) in blacklist'}

    is_string = series.apply(lambda x: isinstance(x, str))

    masks = {}
    masks['invalid_type'] = ~is_string & series.notnull()

    to_validate = series.where(is_string)

    if not nullable:
        masks['isnull'] = to_validate.isnull()
    if unique:
        masks['nonunique'] = to_validate.duplicated() & to_validate.notnull()
    if min_length is not None:
        too_short_dropped = to_validate.dropna().apply(len) < min_length
        masks['too_short'] = pandas.Series(too_short_dropped, series.index)
    if max_length is not None:
        too_long_dropped = to_validate.dropna().apply(len) > max_length
        masks['too_long'] = pandas.Series(too_long_dropped, series.index)
    if case:
        altered_case = getattr(to_validate.str, case)()
        wrong_case_dropped = (
            altered_case.dropna() != to_validate[altered_case.notnull()])
        masks['wrong_case'] = pandas.Series(wrong_case_dropped, series.index)
    if newlines is False:
        masks['newlines'] = to_validate.str.contains(os.linesep)
    if trailing_whitespace is False:
        masks['trailing_space'] = to_validate.str.contains(
            r'^\s|\s$', regex=True)
    if whitespace is False:
        masks['whitespace'] = to_validate.str.contains(r'\s', regex=True)
    if matching_regex:
        masks['regex_mismatch'] = (
            to_validate.str.contains(matching_regex, regex=True)
            .apply(lambda x: x is False) & to_validate.notnull())
    if non_matching_regex:
        masks['regex_match'] = to_validate.str.contains(
            non_matching_regex, regex=True)
    if whitelist is not None:
        masks['not_in_whitelist'] = (
            to_validate.notnull() & ~to_validate.isin(whitelist))
    if blacklist is not None:
        masks['in_blacklist'] = to_validate.isin(blacklist)

    msg_list = _get_error_messages(masks, error_info)

    if len(msg_list) > 0:
        msg = repr(series.name) + ': ' + '; '.join(msg_list) + '.'
        warnings.warn(msg, ValidationWarning, stacklevel=2)

    if return_type is not None:
        return _get_return_object(masks, to_validate, return_type)
