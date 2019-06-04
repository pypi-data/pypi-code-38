#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Posix Backend Archive Module.

Module that implements the abstract_backend_archive class for a posix
backend.
"""
import os
import stat
import shutil
from ...archive_utils import un_abs_path, bytes_type
from ...config import get_config
from ...id2filename import id2filename
from ...exception import ArchiveInterfaceError
from .extendedfile import extended_file_factory
from ..abstract.archive import AbstractBackendArchive


class PosixBackendArchive(AbstractBackendArchive):
    """Posix Backend Archive Class.

    Class that implements the abstract base class for the posix
    archive interface backend.
    """

    def __init__(self, prefix):
        """Constructor for Posix Backend Archive."""
        super(PosixBackendArchive, self).__init__(prefix)
        self._prefix = prefix
        self._file = None
        self._filepath = None
        self._id2filename = lambda x: x
        if get_config().getboolean('posix', 'use_id2filename'):
            self._id2filename = lambda x: id2filename(int(x))

    def open(self, filepath, mode):
        """Open a posix file."""
        # want to close any open files first
        try:
            self.close()
        except ArchiveInterfaceError as ex:
            err_str = "Can't close previous posix file before opening new "\
                      'one with error: ' + str(ex)
            raise ArchiveInterfaceError(err_str)
        try:
            fpath = un_abs_path(self._id2filename(filepath))
            filename = os.path.join(self._prefix, fpath)
            dirname = os.path.dirname(filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname, 0o755)
            self._filepath = filename
            self._file = extended_file_factory(self._filepath, mode)
            return self
        except Exception as ex:
            err_str = "Can't open posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def close(self):
        """Close a posix file."""
        try:
            if self._file:
                self._file.close()
                self._file = None
        except Exception as ex:
            err_str = "Can't close posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def read(self, blocksize):
        """Read a posix file."""
        try:
            if self._file:
                return self._file.read(blocksize)
        except Exception as ex:
            err_str = "Can't read posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        err_str = 'Internal file handle invalid'
        raise ArchiveInterfaceError(err_str)

    def write(self, buf):
        """Write a posix file to the archive."""
        try:
            if self._file:
                # pylint: disable=too-many-function-args
                return self._file.write(bytes_type(buf))
                # pylint: enable=too-many-function-args
        except Exception as ex:
            err_str = "Can't write posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        err_str = 'Internal file handle invalid'
        raise ArchiveInterfaceError(err_str)

    def set_mod_time(self, mod_time):
        """Set the mod time on a posix file."""
        try:
            if self._filepath:
                os.utime(self._filepath, (mod_time, mod_time))
        except Exception as ex:
            err_str = "Can't set posix file mod time with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def set_file_permissions(self):
        """Set the file permissions for a posix file."""
        try:
            if self._filepath:
                os.chmod(self._filepath, 0o444)
        except Exception as ex:
            err_str = "Can't set posix file permissions with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def stage(self):
        """Stage a posix file (no-opt essentially)."""
        try:
            if self._file:
                return self._file.stage()
        except Exception as ex:
            err_str = "Can't stage posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        err_str = 'Internal file handle invalid'
        raise ArchiveInterfaceError(err_str)

    def status(self):
        """Get the status of a posix file."""
        try:
            if self._file:
                return self._file.status()
        except Exception as ex:
            err_str = "Can't get posix file status with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        err_str = 'Internal file handle invalid'
        raise ArchiveInterfaceError(err_str)

    def patch(self, file_id, old_path):
        """Move a posix file."""
        try:
            fpath = un_abs_path(self._id2filename(file_id))
            new_filepath = os.path.join(self._prefix, fpath)
            new_directories = os.path.dirname(new_filepath)
            if not os.path.exists(new_directories):
                os.makedirs(new_directories)

            shutil.move(old_path, new_filepath)
        except Exception as ex:
            err_str = "Can't move posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def remove(self):
        """Remove the file permissions for a posix file."""
        try:
            if self._filepath:
                os.chmod(self._filepath, stat.S_IWRITE)
                os.unlink(self._filepath)
            self._filepath = None
        except Exception as ex:
            err_str = "Can't remove posix file with error: {}".format(ex)
            raise ArchiveInterfaceError(err_str)
