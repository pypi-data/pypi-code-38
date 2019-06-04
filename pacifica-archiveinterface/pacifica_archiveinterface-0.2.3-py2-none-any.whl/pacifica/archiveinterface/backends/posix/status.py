#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Posix Status Module.

Module that implements the Abstract Status class for the posix
archive backend type.
"""

from ..abstract.status import AbstractStatus


class PosixStatus(AbstractStatus):
    """Posix Status Class.

    Class for handling posix status pieces
    needs mtime,ctime, bytes per level array.
    """

    _disk = 'disk'

    def __init__(self, mtime, ctime, bytes_per_level, filesize):
        """Constructor for posix status class."""
        super(PosixStatus, self).__init__(
            mtime,
            ctime,
            bytes_per_level,
            filesize
        )
        self.mtime = mtime
        self.ctime = ctime
        self.bytes_per_level = bytes_per_level
        self.filesize = filesize
        self.filepath = None
        self.defined_levels = self.define_levels()
        self.file_storage_media = self.find_file_storage_media()

    def find_file_storage_media(self):
        """Get the file storage media.  Showed always be disk for posix."""
        level_array = self.defined_levels
        disk_level = 0
        return level_array[disk_level]

    def define_levels(self):
        """Set up what each level definition means."""
        # This defines posix integer levels.  Always disk
        type_per_level = [self._disk]
        return type_per_level

    def set_filepath(self, filepath):
        """Set the filepath that the status is for."""
        self.filepath = filepath
