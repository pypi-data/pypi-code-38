#!/usr/bin/python
# -*- coding: utf-8 -*-
"""HSM Sideband Backend Archive Module.

Module that implements the abstract_backend_archive class for a HSM Sideband
backend.
"""
import os
import stat
import shutil
from ...archive_utils import un_abs_path
from ...config import get_config
from ...exception import ArchiveInterfaceError
from .extended_file_factory import extended_hsmsideband_factory
from ..abstract.archive import AbstractBackendArchive
from ...id2filename import id2filename


def path_info_munge(filepath):
    """Munge the path for this filetype."""
    return_path = un_abs_path(id2filename(int(filepath)))
    return return_path


class HsmSidebandBackendArchive(AbstractBackendArchive):
    """HSM Sideband Backend Archive Class.

    Class that implements the abstract base class for the hsm sideband
    archive interface backend.
    """

    def __init__(self, prefix):
        """Constructor for HSM Sideband Backend Archive."""
        super(HsmSidebandBackendArchive, self).__init__(prefix)
        self._prefix = prefix
        self._file = None
        self._fpath = None
        self._filepath = None
        # since the database prefix may be different then the system the file is mounted on
        self._sam_qfs_prefix = get_config().get(
            'hsm_sideband', 'sam_qfs_prefix')

    def open(self, filepath, mode):
        """Open a hsm sideband file."""
        # want to close any open files first
        try:
            self.close()
        except ArchiveInterfaceError as ex:
            err_str = "Can't close previous HSM Sideband file before opening new "\
                'one with error: ' + str(ex)
            raise ArchiveInterfaceError(err_str)
        try:
            self._fpath = un_abs_path(filepath)
            filename = os.path.join(self._prefix, path_info_munge(self._fpath))
            self._filepath = filename
            # path database refers to, rather then just the file system mount path
            sam_qfs_path = os.path.join(
                self._sam_qfs_prefix, path_info_munge(self._fpath))
            dirname = os.path.dirname(filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname, 0o755)
            self._file = extended_hsmsideband_factory(
                self._filepath, mode, sam_qfs_path)
            return self
        except Exception as ex:
            err_str = "Can't open HSM Sideband file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def close(self):
        """Close a HSM Sideband file."""
        try:
            if self._file:
                self._file.close()
                self._file = None
        except Exception as ex:
            err_str = "Can't close HSM Sideband file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def read(self, blocksize):
        """Read a HSM Sideband file."""
        try:
            if self._file:
                return self._file.read(blocksize)
        except Exception as ex:
            err_str = "Can't read HSM SIdeband file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        err_str = 'Internal file handle invalid'
        raise ArchiveInterfaceError(err_str)

    def write(self, buf):
        """Write a HSM Sideband file to the archive."""
        try:
            if self._file:
                return self._file.write(buf)
        except Exception as ex:
            err_str = "Can't write HSM Sideband file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        err_str = 'Internal file handle invalid'
        raise ArchiveInterfaceError(err_str)

    def set_mod_time(self, mod_time):
        """Set the mod time on a HSM file."""
        try:
            if self._filepath:
                os.utime(self._filepath, (mod_time, mod_time))
        except Exception as ex:
            err_str = "Can't set HSM Sideband file mod time with error: " + \
                str(ex)
            raise ArchiveInterfaceError(err_str)

    def set_file_permissions(self):
        """Set the file permissions for a posix file."""
        try:
            if self._filepath:
                os.chmod(self._filepath, 0o444)
        except Exception as ex:
            err_str = "Can't set HSM Sideband file permissions with error: " + \
                str(ex)
            raise ArchiveInterfaceError(err_str)

    def stage(self):
        """Stage a HSM Sideband file."""
        try:
            if self._file:
                return self._file.stage()
        except Exception as ex:
            err_str = "Can't stage HSM Sideband file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        err_str = 'Internal file handle invalid'
        raise ArchiveInterfaceError(err_str)

    def status(self):
        """Get the status of a HSM Sideband file."""
        try:
            if self._file:
                return self._file.status()
        except Exception as ex:
            err_str = "Can't get HSM Sideband file status with error: " + \
                str(ex)
            raise ArchiveInterfaceError(err_str)
        err_str = 'Internal file handle invalid'
        raise ArchiveInterfaceError(err_str)

    def patch(self, file_id, old_path):
        """Move a hsm file."""
        try:
            fpath = un_abs_path(file_id)
            new_filepath = os.path.join(self._prefix, path_info_munge(fpath))
            new_directories = os.path.dirname(new_filepath)
            if not os.path.exists(new_directories):
                os.makedirs(new_directories)

            shutil.move(old_path, new_filepath)
        except Exception as ex:
            err_str = "Can't move posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def remove(self):
        """Remove the file for a posix file."""
        try:
            if self._filepath:
                os.chmod(self._filepath, stat.S_IWRITE)
                os.unlink(self._filepath)
            self._filepath = None
        except Exception as ex:
            err_str = "Can't remove posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
