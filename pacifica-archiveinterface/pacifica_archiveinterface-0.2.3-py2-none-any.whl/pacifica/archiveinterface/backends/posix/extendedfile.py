#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Extended File Object Module.

Module that Extends the functionality of the base file object

to import:

>>> import ExtendedFile
>>> from extendedfile import ExtendedFile
>>> ExtendedFile(path, mode)
"""
import os
from six import PY2
from ...archive_utils import int_type
from .status import PosixStatus


def extended_file_factory(filepath, mode):
    """Return appropiate binary io object with additional methods."""
    if PY2:  # pragma: no cover only one version of python
        # pylint: disable=undefined-variable
        file_obj_cls = file  # noqa
        # pylint: enable=undefined-variable
    elif 'r' in mode:  # pragma: no cover only one version of python
        from io import BufferedReader
        file_obj_cls = BufferedReader
    else:  # pragma: no cover only one version of python
        from io import BufferedWriter
        file_obj_cls = BufferedWriter

    class ExtendedFile(file_obj_cls):
        """Extending default file stuct to support additional methods."""

        def __init__(self, filepath, mode, *args, **kwargs):
            """Set some additional attributes to support staging."""
            if PY2:  # pragma: no cover only one version of python
                super(ExtendedFile, self).__init__(
                    filepath, mode, *args, **kwargs)
            else:  # pragma: no cover only one version of python
                from io import FileIO
                file_obj = FileIO(filepath, mode)
                super(ExtendedFile, self).__init__(file_obj)
            self._path = filepath
            self._staged = True

        def status(self):
            """Return status of file. Since POSIX, will always return disk."""
            mtime = os.path.getmtime(self._path)
            ctime = os.path.getctime(self._path)
            bytes_per_level = (int_type(os.path.getsize(self._path)),)
            filesize = os.path.getsize(self._path)
            status = PosixStatus(mtime, ctime, bytes_per_level, filesize)
            status.set_filepath(self._path)

            return status

        def stage(self):
            """Stage a file. Since POSIX, essentially a no op."""
            self._staged = True
    return ExtendedFile(filepath, mode)
