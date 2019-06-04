#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Group of utility functions.

Used in various parts of the archive interface.
"""
import email.utils as eut
import time
from os import path
from six import integer_types, PY2
from .exception import ArchiveInterfaceError

# pylint: disable=invalid-name
if PY2:  # pragma: no cover
    bytes_type = str
else:  # pragma: no cover only will work on one version of python
    def bytes_type(unicode_obj):
        """Convert the unicode object into bytes."""
        if isinstance(unicode_obj, bytes):
            return unicode_obj
        return bytes(unicode_obj, 'UTF-8')
int_type = integer_types[-1]
# pylint: enable=invalid-name


def file_status(status, response):
    """Response for when file is on the hpss system."""
    response_headers = [
        ('X-Pacifica-Messsage', 'File was found' if status else 'File Not found'),
        ('X-Pacifica-File', str(getattr(status, 'filepath', 'File Not Found'))),
        ('X-Content-Length', str(getattr(status, 'filesize', 'File Not Found'))),
        ('Last-Modified', str(getattr(status, 'mtime', 'File Not Found'))),
        ('X-Pacifica-Ctime', str(getattr(status, 'ctime', 'File Not Found'))),
        (
            'X-Pacifica-Bytes-Per-Level',
            str(getattr(status, 'bytes_per_level', 'File Not Found'))
        ),
        (
            'X-Pacifica-File-Storage-Media',
            str(getattr(status, 'file_storage_media', 'File Not Found'))
        ),
        ('Content-Type', 'application/json')
    ]
    response.status = '204 No Content' if status else '404 Not Found'
    for key, value in response_headers:
        response.headers[key] = value


def un_abs_path(path_name):
    """Remove absolute path piece."""
    try:
        if path.isabs(path_name):
            path_name = path_name[1:]
        return path_name
    except (AttributeError, TypeError) as ex:
        raise ArchiveInterfaceError('Cant remove absolute path: ' + str(ex))


def get_http_modified_time(env):
    """Get the modified time from the request in unix timestamp.

    Returns current time if no time was passed.
    """
    try:
        mod_time = None
        if 'HTTP_LAST_MODIFIED' in env:
            mod_time = eut.mktime_tz(
                eut.parsedate_tz(env['HTTP_LAST_MODIFIED']))
        else:
            mod_time = time.time()
        return mod_time
    except (TypeError, IndexError, AttributeError) as ex:
        raise ArchiveInterfaceError('Cant parse the files modtime: ' + str(ex))
