#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module that has the abstract class for a file's status."""
import abc


class AbstractStatus(object):
    """Abstract Base Class for Status.

    Child backend objects need to implement the following
    methods to allow file status to function.
    """

    __metaclass__ = abc.ABCMeta

    mtime = None
    ctime = None
    bytes_per_level = None
    filesize = None
    defined_levels = None
    file_storage_media = None
    filepath = None

    @abc.abstractmethod
    def __init__(self, mtime, ctime, bytes_per_level, filesize):
        """Constructor for AbstractClass.

        Implemented versions of this class need to set all the
        attributes defined in this abstract class.
        """
        pass

    @abc.abstractmethod
    def find_file_storage_media(self):
        """Find File Storage Media.

        Method that finds the media the file in the archive
        backend is stored on.  Usually disk or tape.
        """
        pass

    @abc.abstractmethod
    def define_levels(self):
        """Defined list of levels.

        Method that defines the storage levels in the archive
        backend. So a backend archive with a disk, tape, and error drive
        will return the following ["disk", "tape", "error"].
        """
        pass

    @abc.abstractmethod
    def set_filepath(self, filepath):
        """Set File Path.

        Method that sets the filepath class attribute.  Used
        to return the correct status of a file.
        """
        pass
