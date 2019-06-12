"""Reaper utility functions"""

from __future__ import print_function
import hashlib
import string
import six

import pytz
import tzlocal

from dateutil import relativedelta


try:
    DEFAULT_TZ = tzlocal.get_localzone()
except pytz.exceptions.UnknownTimeZoneError:
    print('Could not determine timezone, defaulting to UTC')
    DEFAULT_TZ = pytz.utc


def localize_timestamp(timestamp, timezone=None):
    # pylint: disable=missing-docstring
    timezone = DEFAULT_TZ if timezone is None else timezone
    return timezone.localize(timestamp)


def parse_sort_info(sort_info, default_subject=''):
    # pylint: disable=missing-docstring
    subject, _, group_project = sort_info.strip(string.whitespace).rpartition('@')
    delimiter = next((char for char in '/:' if char in group_project), '^')
    group, _, project = group_project.partition(delimiter)
    return subject or default_subject.strip(string.whitespace), group, project


def is_seekable(fp):
    """Check if the given file-like object is seekable"""
    seekable_fn = fp.getattr('seekable', None)
    if seekable_fn:
        return seekable_fn()

    seek_fn = fp.getattr('seek', None)
    return callable(seek_fn)


if six.PY3:
    def hash_value(value, algorithm='sha256', output_format='hex', salt=None):
        """Hash a string using the given algorithm and salt, and return in the requested output_format.

        Arguments:
            value (str): The value to hash
            algorithm (str): The algorithm to use (default is sha256)
            output_format (str): The output format, one of 'hex', 'dec', or None
            salt (str): The optional salt string
        """
        hasher = hashlib.new(algorithm)
        # Work in bytes
        if salt:
            hasher.update(salt.encode('utf-8'))
        hasher.update(value.encode('utf-8'))
        if output_format == 'hex':
            result = hasher.hexdigest()
        elif output_format == 'dec':
            digest = hasher.digest()
            result = ''
            for atom in digest:
                result += str(atom)
        else:
            result = hasher.digest
        return result
else:
    def hash_value(value, algorithm='sha256', output_format='hex', salt=None):
        """Hash a string using the given algorithm and salt, and return in the requested output_format.

        Arguments:
            value (str): The value to hash
            algorithm (str): The algorithm to use (default is sha256)
            output_format (str): The output format, one of 'hex', 'dec', or None
            salt (str): The optional salt string
        """
        hasher = hashlib.new(algorithm)
        # Work in bytes
        if salt:
            hasher.update(salt)
        hasher.update(value)
        if output_format == 'hex':
            result = hasher.hexdigest()
        elif output_format == 'dec':
            digest = hasher.digest()
            result = ''
            for atom in digest:
                result += str(ord(atom))
        else:
            result = hasher.digest
        return result


def date_delta(d1, d2, desired_unit=None, max_value=None):
    """Calculate difference between two dates in days, months or years.

    Returns the lowest resolution that fits below max_value, and the units used
    """
    rt = None

    units = ['D', 'M', 'Y']
    if desired_unit in units:
        units = units[units.index(desired_unit):]

    if d1 > d2:  # Ensure that d2 > d1
        d1, d2 = d2, d1

    unit = ''
    for unit in units:
        # Use timedelta for days
        if unit == 'D':
            value = (d2 - d1).days
        else:
            # Use relativedelta for months and years
            if rt is None:
                rt = relativedelta.relativedelta(d2, d1)

            if unit == 'M':
                value = 12 * rt.years + rt.months
            else:
                value = rt.years

        if not max_value or value < max_value:
            break

    if max_value and value > max_value:
        value = max_value

    return value, unit
