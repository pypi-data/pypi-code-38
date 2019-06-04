#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module that allows for the extension of the hsm sideband archive."""
import os
from six import PY2
from ...archive_utils import int_type
from .status import HsmSidebandStatus
from .orm import SamInode, SamFile, SamPath


def extended_hsmsideband_factory(filepath, mode, sam_qfs_path):
    """Return appropiate binary io object with additional methods."""
    if PY2:  # pragma: no cover only one version of python
        # pylint: disable=undefined-variable
        file_obj_cls = file  # noqa
        # pylint: enable=undefined-variable
    elif 'r' in mode:
        from io import BufferedReader
        file_obj_cls = BufferedReader
    else:
        from io import BufferedWriter
        file_obj_cls = BufferedWriter

    class ExtendedHsmSideband(file_obj_cls):
        """Extending default file stuct to support additional methods."""

        def __init__(self, filepath, mode, sam_qfs_path):
            """Extended HSM Sideband Constructor."""
            if PY2:  # pragma: no cover only one version of python
                super(ExtendedHsmSideband, self).__init__(filepath, mode)
            else:
                from io import FileIO
                file_obj = FileIO(filepath, mode)
                super(ExtendedHsmSideband, self).__init__(file_obj)
            self._path = filepath
            self._sam_qfs_path = sam_qfs_path

        def status(self):
            """Return status of file."""
            filename = os.path.basename(self._sam_qfs_path)
            # need to add a slash for sideband db
            directory = os.path.dirname(self._sam_qfs_path) + '/'
            stat_record = self._stat_ino_sql(filename, directory)
            if stat_record:
                mtime = stat_record['mtime']
                ctime = stat_record['ctime']
                # if the record is online then on disk, else say not on disk but on tape
                if stat_record['online'] == 1:
                    bytes_per_level = (int_type(stat_record['size']),)
                else:
                    bytes_per_level = (
                        int_type(0), int_type(stat_record['size']))
                filesize = stat_record['size']
                status = HsmSidebandStatus(
                    mtime, ctime, bytes_per_level, filesize)
                status.set_filepath(self._path)
                return status
            return None

        def stage(self):
            """Stage a file. HSM stages a file when a read call is made."""
            self.read(1024)

        def _stat_ino_sql(self, fname, directory):
            """Return the record for specified file and directory."""
            SamInode.database_connect()
            # pylint: disable=no-member
            result = (
                SamInode.select()
                .join(SamFile, on=(SamFile.ino == SamInode.ino))
                .join(SamPath, on=(SamPath.ino == SamFile.p_ino))
                .where(SamPath.path == str(directory), SamFile.name == str(fname))
                .get()
            )
            # pylint: enable=no-member
            SamInode.database_close()

            if result:
                return self._make_status_dictionary(result)
            return None

        @staticmethod
        def _make_status_dictionary(result):
            """Break the query results into a dictionary."""
            status = {'ino': result.ino, 'size': result.size, 'ctime': result.create_time,
                      'mtime': result.modify_time, 'online': result.online}
            return status
    return ExtendedHsmSideband(filepath, mode, sam_qfs_path)
