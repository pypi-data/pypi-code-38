"""Provides functions for parsing parrec header files"""
import datetime
import logging
import re
from . import util
from .parrec_headers import HEADER_KEY_DICT

log = logging.getLogger(__name__)

RE_KEY_NAME = re.compile(r'^([-\.\w\s]+)\s*.*$')
RE_KEY_SUB = re.compile(r'[-_\s\.]+')

PAR_DATETIME_FORMAT = '%Y.%m.%d / %H:%M:%S'


def parse_par_header(fileobj):
    """Parse the PAR header file, extracting keys

    Arguments:
        fileobj (file): The file-like object that supports readlines, opened in utf-8
    """
    result = {}

    for line in fileobj.readlines():
        # Property lines begin with a '.'
        if len(line) < 2 or line[0] != '.':
            # Ignore everything else
            continue

        # Partition the line on ':', and strip the key
        key, part, value = line.partition(':')
        if not part:
            continue

        # NOTE: Right now we only use the HEADER_KEY_DICT to get a normalized key name
        # We could also make use of the type info available in HEADER_KEY_DICT
        key = key[1:].strip()
        param = HEADER_KEY_DICT.get(key)
        if param:
            key = param[0]
        else:
            # Convert the key name
            key_match = RE_KEY_NAME.match(key)
            if key_match is None:
                log.debug('Invalid PAR key name: %s', key)
                continue

            key = RE_KEY_SUB.sub('_', key_match.group(1).strip()).lower()

        result[key] = value.strip()

    return result


def parse_par_timestamp(value, timezone=None):
    """Convert a PAR timestamp to a datetime object.

    Arguments:
        value (str): The string value to convert
        timezone (obj): The optional timezone to use (otherwise DEFAULT_TZ will be used)

    Returns:
        datetime: The converted date time
    """
    return util.localize_timestamp(datetime.datetime.strptime(value, PAR_DATETIME_FORMAT), timezone)
