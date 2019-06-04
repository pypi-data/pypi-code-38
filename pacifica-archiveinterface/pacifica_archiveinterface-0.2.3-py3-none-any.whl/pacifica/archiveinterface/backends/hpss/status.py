#!/usr/bin/python
# -*- coding: utf-8 -*-
"""HPSS Status Module.

Module that implements the Abstract Status class for the hpss
archive backend type.
"""

from ..abstract.status import AbstractStatus


class HpssStatus(AbstractStatus):
    """HPSS Status Class.

    Class for handling hpss status pieces
    needs mtime,ctime, bytes per level array.
    """

    _disk = 'disk'
    _tape = 'tape'
    _error = 'error'

    def __init__(self, mtime, ctime, bytes_per_level, filesize):
        """HPSS Status Constructor."""
        super(HpssStatus, self).__init__(
            mtime, ctime, bytes_per_level, filesize
        )
        self.mtime = mtime
        self.ctime = ctime
        self.bytes_per_level = bytes_per_level
        self.filesize = filesize
        self.defined_levels = self.define_levels()
        self.file_storage_media = self.find_file_storage_media()
        self.filepath = None

    def find_file_storage_media(self):
        """Set if file is on disk or tape."""
        level_array = self.defined_levels
        level = 0
        for num_bytes in self.bytes_per_level:
            if num_bytes == self.filesize:
                break
            level += 1

        return level_array[level]

    def define_levels(self):
        """Set up what each level definition means."""
        # This defines what hpss integer levels really mean
        # handle error if on level 4 or 5 since those are suppose to be null
        # UPDATE LEVEL NAMES AS NEEDED
        type_per_level = [self._disk, self._tape, self._tape,
                          self._error, self._error]
        return type_per_level

    def set_filepath(self, filepath):
        """Set the filepath that the status is for."""
        self.filepath = filepath
